# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
import traceback

from ansible.module_utils.six import raise_from
from ansible.errors import AnsibleError

# Pull in requests
REQUESTS_IMP_ERR = None
try:
    import requests
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()

class HTTPBearerAuth(requests.auth.AuthBase):
    """A :class:`requests.auth` bearer token authentication method
    per https://2.python-requests.org/en/master/user/authentication/#new-forms-of-authentication

    :param token: Bearer token to be used instead of user/pass or session
    """

    def __init__(self, token):
        self.token = token
        if REQUESTS_IMP_ERR:
            raise_from(
                AnsibleError('requests must be installed to use this plugin'),
                REQUESTS_IMP_ERR)

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer {0}".format(str(self.token))
        return r
