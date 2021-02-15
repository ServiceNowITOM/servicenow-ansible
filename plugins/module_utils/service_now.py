# -*- coding: utf-8 -*-
# Copyright: (c) 2019-2021, Ansible Project
# Copyright: (c) 2017, Tim Rightnour <thegarbledone@gmail.com>
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import requests
import traceback

from ansible.module_utils.basic import AnsibleModule, env_fallback, missing_required_lib
from ansible_collections.n3pjk.servicenow.plugins.module_utils.bearerauth import BearerAuth

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
        # Initialize instance arguments
        if required_together is None:
            required_together = [
                ['username', 'password'],
                ['username', 'password', 'client_id', 'client_secret'],
                ['username', 'password', 'client_id', 'client_secret', 'token'],
            ]
        else:
            required_together += [
                ['username', 'password'],
                ['username', 'password', 'client_id', 'client_secret'],
                ['username', 'password', 'client_id', 'client_secret', 'token'],
            ]

        if mutually_exclusive is None:
            mutually_exclusive = [
                ['host', 'instance'],
            ]
        else:
            mutually_exclusive += [
                ['host', 'instance'],
            ]

        if required_one_of is None:
            required_one_of = [
                ['host', 'instance'],
            ]
        else:
            required_one_of += [
                ['host', 'instance'],
            ]

        # Output of module
        self.result = {}

        # Session tracking information
        self.session = {'token': None}

        # Authenticated connection
        self.connection = None

        # Initialize AnsibleModule superclass before params
        super(ServiceNowModule, self).__init__(
            required_together,
            mutually_exclusive,
            required_one_of,
            *args,
            **kwargs
        )

        if not HAS_PYSNOW:
            AnsibleModule.fail_json(
                msg=missing_required_lib('pysnow'),
                exception=PYSNOW_IMP_ERR
            )

        # Params
        #
        # REQUIRED: Their absence will chuck a rod
        #   None
        # OPTIONAL: Use params.get() to gracefully fail
        self.instance = self.params.get('instance')
        self.host = self.params.get('host')
        self.auth = self.params.get('auth')
        self.username = self.params.get('username')
        self.password = self.params.get('password')
        self.client_id = self.params.get('client_id')
        self.client_secret = self.params.get('client_secret')
        self.token = self.params.get('token')

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

    def _auth_oauth(self):
        try:
            self.connection = pysnow.OAuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_updater=self._token_updater,
                instance=self.instance,
                host=self.host
            )
        except Exception as detail:
            self.fail(
                msg='Could not connect to ServiceNow: {0}'.format(
                    str(detail)
                )
            )
        if not self.session['token']:
            # No previous token exists, Generate new.
            try:
                self.session['token'] = self.connection.generate_token(
                    self.username,
                    self.password
                )
            except pysnow.exceptions.TokenCreateError as detail:
                self.fail(
                    msg='Unable to generate a new token: {0}'.format(
                        str(detail)
                    )
                )
            self.connection.set_token(self.session['token'])

    def _auth_token(self):
        try:
            s = requests.Session()
            s.auth = BearerAuth(self.token)
            self.connection = pysnow.Client(
                instance=self.instance,
                host=self.host,
                user=self.username,
                password=self.password,
                session=s
            )
        except Exception as detail:
            self.fail(
                msg='Could not connect to ServiceNow: {0}'.format(
                    str(detail)
                )
            )

    def _auth_okta(self):
        self.fail(msg='Okta authentication module not yet implemented.')

    def _token_updater(self, new_token):
        self.session['token'] = new_token
        self.connection = pysnow.OAuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_updater=self._token_updater,
            instance=self.instance,
            host=self.host
        )
        try:
            self.connection.set_token(self.session['token'])
        except pysnow.exceptions.MissingToken:
            self.module.fail(msg="Token is missing")
        except Exception as detail:
            self.module.fail(
                msg='Could not refresh token: {0}'.format(
                    str(detail)
                )
            )

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
        )
        return argument_spec
