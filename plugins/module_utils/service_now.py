# -*- coding: utf-8 -*-
# Copyright: (c) 2019-2021, Ansible Project
# Copyright: (c) 2017, Tim Rightnour <thegarbledone@gmail.com>
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
import requests
import traceback
import logging

from ansible.module_utils.basic import AnsibleModule, env_fallback, missing_required_lib
from ansible_collections.n3pjk.servicenow.plugins.module_utils.httpbearerauth import HTTPBearerAuth

# Pull in pysnow
HAS_PYSNOW = False
PYSNOW_IMP_ERR = None
try:
    import pysnow
    HAS_PYSNOW = True
except ImportError:
    PYSNOW_IMP_ERR = traceback.format_exc()


class ServiceNowModule(AnsibleModule):

    def __init__(self, required_together=None, mutually_exclusive=None, required_one_of=None, *args, **kwargs):
        ''' Constructor - This module mediates interactions with Service Now.

        :module: ServiceNowModule extended from AnsibleModule.
        '''

        # Turn on debugging
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug on for pysnow in ServiceNowModule.")

        # Initialize instance arguments
        self._required_together = [
            ['username', 'password'],
            ['client_id', 'client_secret'],
        ]
        if required_together is None:
            self.required_together = self._required_together
        else:
            self.required_together.append(self._required_together)

        self._mutually_exclusive = [
            ['host', 'instance'],
        ]
        if mutually_exclusive is None:
            self.mutually_exclusive = self._mutually_exclusive
        else:
            self.mutually_exclusive.append(self._mutually_exclusive)

        self._required_one_of = [
            ['host', 'instance'],
        ]
        if required_one_of is None:
            self.required_one_of = self._required_one_of
        else:
            self.required_one_of.append(self._required_one_of)

        # Initialize AnsibleModule superclass before params
        super(ServiceNowModule, self).__init__(
            required_together=self.required_together,
            mutually_exclusive=self.mutually_exclusive,
            required_one_of=self.required_one_of,
            *args,
            **kwargs
        )

        # Output of module
        self.result = {}

        # Okta information
        self.okta = {
            'domain': None,
            'server': None,
            'mode': None,
            'scope': None,
            # Endpoints
            # /authorize is used for browser-based auth, so it and /keys are not
            # needed. We don't maintain state, so ignore /logout and /revoke too.
            # Nor do we need any well-known endpoints.
            'url': {
                'base': None,
                'introspect': None,
                'token': None,
                'user': None,
            },
        }

        # Authenticated connection
        self.connection = None

        if not HAS_PYSNOW:
            AnsibleModule.fail_json(
                self,
                msg=missing_required_lib('pysnow'),
                exception=PYSNOW_IMP_ERR
            )

        # Params
        #
        # REQUIRED: Their absence will chuck a rod
        self.auth = self.params['auth']
        # OPTIONAL: Use params.get() to gracefully fail
        self.instance = self.params.get('instance')
        self.host = self.params.get('host')
        self.username = self.params.get('username')
        self.password = self.params.get('password')
        self.client_id = self.params.get('client_id')
        self.client_secret = self.params.get('client_secret')
        self.token = self.params.get('token')
        # OKTA
        self.okta['domain'] = self.params.get('okta_domain')
        self.okta['server'] = self.params.get('okta_server')
        self.okta['scope'] = self.params.get('okta_scope')

        # Turn on debug if not specified, but ANSIBLE_DEBUG is set
        self.module_debug = {}
        if self._debug:
            self.warn('Enable debug output because ANSIBLE_DEBUG was set.')
            self.params['log_level'] = 'debug'
        self.log_level = self.params['log_level']

        # Log into Service Now
        self._login()

    # Debugging
    #
    # Tools to handle debugging output from the APIs.
    def _mod_debug(self, key, **kwargs):
        self.module_debug[key] = kwargs
        if 'module_debug' not in self.module_debug:
            self.module_debug = dict(key=kwargs)
        else:
            self.module_debug.update(key=kwargs)

    # Login
    #
    # Connect using the method specified by 'auth'
    def _login(self):
        self.result['changed'] = False
        if self.params['auth'] == 'basic':
            self._auth_basic()
        elif self.params['auth'] == 'oauth':
            self._auth_oauth()
        elif self.params['auth'] == 'token':
            self._auth_token()
        elif self.params['auth'] == 'okta':
            self._auth_okta()
        else:
            self.fail(
                msg="Auth method not implemented: {0}".format(
                    self.params['auth']
                )
            )

    # Basic
    #
    # Connect using username and password
    def _auth_basic(self):
        try:
            self.connection = pysnow.Client(
                instance=self.instance,
                host=self.host,
                user=self.username,
                password=self.password
            )
        except Exception as detail:
            self.module.fail(
                msg='Could not connect to ServiceNow: {0}'.format(
                    str(detail)
                )
            )

    # OAuth
    #
    # Connect using client id and secret in addition to Basic
    def _auth_oauth(self):
        try:
            self.connection = pysnow.OAuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_updater=self._oauth_token_updater,
                instance=self.instance,
                host=self.host
            )
        except Exception as detail:
            self.fail(
                msg='Could not connect to ServiceNow: {0}'.format(
                    str(detail)
                )
            )
        if not self.token:
            # No previous token exists, Generate new.
            try:
                self.token = self.connection.generate_token(
                    self.username,
                    self.password
                )
            except pysnow.exceptions.TokenCreateError as detail:
                self.fail(
                    msg='Unable to generate a new token: {0}'.format(
                        str(detail)
                    )
                )
            self.connection.set_token(self.token)

    def _oauth_token_updater(self, new_token):
        self.token = new_token
        self.connection = pysnow.OAuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_updater=self._token_updater,
            instance=self.instance,
            host=self.host
        )
        try:
            self.connection.set_token(self.token)
        except pysnow.exceptions.MissingToken:
            self.module.fail(msg="Token is missing")
        except Exception as detail:
            self.module.fail(
                msg='Could not refresh token: {0}'.format(
                    str(detail)
                )
            )

    # Token
    #
    # Use a supplied token instead of client id and secret.
    def _auth_token(self):
        try:
            s = requests.Session()
            s.auth = HTTPBearerAuth(self.token)
            self.connection = pysnow.Client(
                instance=self.instance,
                host=self.host,
                session=s
            )
        except Exception as detail:
            self.fail(
                msg='Could not connect to ServiceNow: {0}'.format(
                    str(detail)
                )
            )

    # Okta
    #
    # Use the Okta OpenID protocol to obtain a bearer token.
    def _auth_okta(self):
        if self.okta['domain']:
            self.okta['url']['base'] = "https://{0}/oauth2".format(
                self.okta['domain'])
            # Okta in Single Sign-On mode
            self.okta['mode'] = 'SSO'
        else:
            self.fail(msg='auth=okta requires okta_domain be specified.')
        if self.okta['server']:
            self.okta['url']['base'] = "{0}/{1}".format(
                self.okta['url']['base'], self.okta['server'])
            # Okta in Custom Authorization Server mode
            self.okta['mode'] = 'CAS'
        self.okta['url']['introspect'] = "{0}/v1/introspect".format(
            self.okta['url']['base'])
        self.okta['url']['token'] = "{0}/v1/token".format(
            self.okta['url']['base'])
        self.okta['url']['user'] = "{0}/v1/userinfo".format(
            self.okta['url']['base'])

        if self.token is None:
            self.token = self._okta_get_token()
        else:
            self._okta_inspect_token()
            if self.result['okta']['active'] != 'true':
                self.token = self._okta_get_token()
        self._auth_token()

    def _okta_get_token(self):
        r = requests.post(
            self.okta['url']['token'],
            auth=(self.client_id, self.client_secret),
            headers={
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'password',
                'username': self.username,
                'password': self.password,
                'scope': self.okta['scope']
            }
        )
        self._okta_response(r)
        self._okta_inspect_token()
        self._okta_inspect_user()
        return self.result['okta']['id_token']

    def _okta_inspect_token(self):
        r = requests.post(
            self.okta['url']['introspect'],
            auth=(self.client_id, self.client_secret),
            headers={
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded'
            },
            params={
                'token': self.token,
                'token_type_hint': 'id_token'
            }
        )
        self._okta_response(r)

    def _okta_inspect_user(self):
        if 'access_token' in self.result['okta']:
            r = requests.post(
                self.okta['url']['user'],
                auth=HTTPBearerAuth(self.result['okta']['access_token'])
            )
            self._okta_response(r)

    def _okta_response(self, r):
        r.raise_for_status()
        if 'okta' not in self.result:
            self.result['okta'] = r.json()
        else:
            self.result['okta'].update(r.json())

    #
    # Extend AnsibleModule methods
    #

    def fail(self, msg):
        if self.log_level == 'debug':
            pass
        AnsibleModule.fail_json(self, msg=msg, **self.result)

    def exit(self):
        '''Called to end module'''
        if 'invocation' not in self.result:
            self.result['invocation'] = {
                'module_args': self.params,
                #               'module_kwargs': {
                #                  'ServiceNowModuleKWArgs': self.ServiceNowModuleKWArgs,
                #               }
            }
        if self.log_level == 'debug':
            if self.module_debug:
                self.result['invocation'].update(
                    module_debug=self.module_debug)
        AnsibleModule.exit_json(self, **self.result)

    def _merge_dictionaries(self, a, b):
        new = a.copy()
        new.update(b)
        return new

    @staticmethod
    def create_argument_spec():
        argument_spec = dict(
            auth=dict(
                type='str',
                choices=[
                    'basic',
                    'oauth',
                    'token',
                    'okta',
                ],
                default='basic',
                fallback=(
                    env_fallback,
                    ['SN_AUTH']
                )
            ),
            log_level=dict(
                type='str',
                choices=[
                    'debug',
                    'info',
                    'normal',
                ],
                default='normal'
            ),
            instance=dict(
                type='str',
                required=False,
                fallback=(
                    env_fallback,
                    ['SN_INSTANCE']
                )
            ),
            host=dict(
                type='str',
                required=False,
                fallback=(
                    env_fallback,
                    ['SN_HOST']
                )
            ),
            username=dict(
                type='str',
                required=False,
                fallback=(
                    env_fallback,
                    ['SN_USERNAME']
                )
            ),
            password=dict(
                type='str',
                required=False,
                no_log=True,
                fallback=(
                    env_fallback,
                    ['SN_PASSWORD']
                )
            ),
            client_id=dict(
                type='str',
                required=False,
                no_log=True,
                fallback=(
                    env_fallback,
                    ['SN_CLIENTID']
                )
            ),
            client_secret=dict(
                type='str',
                required=False,
                no_log=True,
                fallback=(
                    env_fallback,
                    ['SN_CLIENTSECRET']
                )
            ),
            token=dict(
                type='str',
                required=False,
                no_log=True,
                fallback=(
                    env_fallback,
                    ['SN_TOKEN']
                )
            ),
            okta_domain=dict(
                type='str',
                required=False,
                fallback=(
                    env_fallback,
                    ['OKTA_DOMAIN']
                )
            ),
            okta_server=dict(
                type='str',
                required=False,
                fallback=(
                    env_fallback,
                    ['OKTA_SERVER']
                )
            ),
            # No codes means offline_access is not available.
            okta_scope=dict(
                type='list',
                elements='str',
                required=False,
                fallback=(
                    env_fallback,
                    ['OKTA_SCOPE']
                )
            ),
        )
        return argument_spec
