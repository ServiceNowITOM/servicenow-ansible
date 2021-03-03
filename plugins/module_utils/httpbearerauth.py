# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
import traceback

# Pull in requests
HAS_REQUESTS = False
REQUESTS_IMP_ERR = None
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()

class HTTPBearerAuth(requests.auth.AuthBase):
    """A :class:`requests.auth` bearer token authentication method
    per https://2.python-requests.org/en/master/user/authentication/#new-forms-of-authentication

    :param token: Bearer token to be used instead of user/pass or session
    """

    def __init__(self, token):
        self.token = token
        if not HAS_REQUESTS:
            self.fail(self, msg=missing_required_lib('requests'),
                      exception=REQUESTS_IMP_ERR)

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer {0}".format(str(self.token))
        return r
