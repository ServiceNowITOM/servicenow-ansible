#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Tim Rightnour <thegarbledone@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: snow_record
short_description: Manage records in ServiceNow
description:
    - Creates, deletes and updates a single record in ServiceNow.
options:
    table:
      description:
      - Table to query for records.
      required: false
      default: incident
      type: str
    state:
      description:
      - If C(present) is supplied with a C(number) argument, the module will attempt to update the record with the supplied data.
      - If no such record exists, a new one will be created.
      - C(absent) will delete a record.
      choices: [ present, absent ]
      required: true
      type: str
    data:
      description:
      - key, value pairs of data to load into the record. See Examples.
      - Required for C(state:present).
      type: dict
    number:
      description:
      - Record number to update.
      - Required for C(state:absent).
      required: false
      type: str
    lookup_field:
      description:
      - Changes the field that C(number) uses to find records.
      required: false
      default: number
      type: str
    attachment:
      description:
      - Attach a file to the record.
      required: false
      type: str
requirements:
    - python pysnow (pysnow)
author:
    - Tim Rightnour (@garbled1)
extends_documentation_fragment:
- servicenow.servicenow.service_now.documentation

'''

EXAMPLES = r'''
- name: Grab a user record
  servicenow.servicenow.snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: present
    number: 62826bf03710200044e0bfc8bcbe5df1
    table: sys_user
    lookup_field: sys_id

- name: Grab a user record using OAuth
  servicenow.servicenow.snow_record:
    username: ansible_test
    password: my_password
    client_id: "1234567890abcdef1234567890abcdef"
    client_secret: "Password1!"
    instance: dev99999
    state: present
    number: 62826bf03710200044e0bfc8bcbe5df1
    table: sys_user
    lookup_field: sys_id

- name: Create an incident
  servicenow.servicenow.snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: present
    data:
      short_description: "This is a test incident opened by Ansible"
      severity: 3
      priority: 2
  register: new_incident

- name: Create an incident using host instead of instance
  servicenow.servicenow.snow_record:
    username: ansible_test
    password: my_password
    host: dev99999.mycustom.domain.com
    state: present
    data:
      short_description: "This is a test incident opened by Ansible"
      priority: 2

- name: Delete the record we just made
  servicenow.servicenow.snow_record:
    username: admin
    password: xxxxxxx
    instance: dev99999
    state: absent
    number: "{{new_incident['record']['number']}}"

- name: Delete a non-existant record
  servicenow.servicenow.snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: absent
    number: 9872354
  failed_when: false

- name: Update an incident
  servicenow.servicenow.snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: present
    number: INC0000055
    data:
      work_notes : "Been working all day on this thing."

- name: Attach a file to an incident
  servicenow.servicenow.snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: present
    number: INC0000055
    attachment: README.md
  tags: attach
'''

RETURN = r'''
record:
   description: Record data from Service Now
   type: dict
   returned: when supported
attached_file:
   description: Details of the file that was attached via C(attachment)
   type: dict
   returned: when supported
'''

import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native
from ansible_collections.servicenow.servicenow.plugins.module_utils.service_now import ServiceNowClient

try:
    # This is being handled by ServiceNowClient
    import pysnow
except ImportError:
    pass


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = ServiceNowClient.snow_argument_spec()
    module_args.update(
        table=dict(type='str', required=False, default='incident'),
        state=dict(choices=['present', 'absent'],
                   type='str', required=True),
        number=dict(default=None, required=False, type='str'),
        data=dict(default=None, required=False, type='dict'),
        lookup_field=dict(default='number', required=False, type='str'),
        attachment=dict(default=None, required=False, type='str')
    )
    module_required_together = [
        ['client_id', 'client_secret']
    ]
    module_required_if = [
        ['state', 'absent', ['number']],
    ]

    module_mutually_exclusive = [
        ['host', 'instance'],
    ]

    module_required_one_of = [
        ['host', 'instance'],
    ]

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=module_required_together,
        required_if=module_required_if,
        required_one_of=module_required_one_of,
        mutually_exclusive=module_mutually_exclusive,
    )

    # Connect to ServiceNow
    service_now_client = ServiceNowClient(module)
    service_now_client.login()
    conn = service_now_client.conn

    params = module.params
    instance = params['instance']
    host = params['host']
    table = params['table']
    state = params['state']
    number = params['number']
    data = params['data']
    lookup_field = params['lookup_field']

    result = dict(
        changed=False,
        instance=instance,
        host=host,
        table=table,
        number=number,
        lookup_field=lookup_field
    )

    # check for attachments
    if params['attachment'] is not None:
        attach = params['attachment']
        b_attach = to_bytes(attach, errors='surrogate_or_strict')
        if not os.path.exists(b_attach):
            module.fail_json(msg="Attachment {0} not found".format(attach))
        result['attachment'] = attach
    else:
        attach = None

    # Deal with check mode
    if module.check_mode:

        # if we are in check mode and have no number, we would have created
        # a record.  We can only partially simulate this
        if number is None:
            result['record'] = dict(data)
            result['changed'] = True

        # do we want to check if the record is non-existent?
        elif state == 'absent':
            try:
                record = conn.query(table=table, query={lookup_field: number})
                res = record.get_one()
                result['record'] = dict(Success=True)
                result['changed'] = True
            except pysnow.exceptions.NoResults:
                result['record'] = None
            except Exception as detail:
                module.fail_json(msg="Unknown failure in query record: {0}".format(to_native(detail)), **result)

        # Let's simulate modification
        else:
            try:
                record = conn.query(table=table, query={lookup_field: number})
                res = record.get_one()
                for key, value in data.items():
                    res[key] = value
                    result['changed'] = True
                result['record'] = res
            except pysnow.exceptions.NoResults:
                snow_error = "Record does not exist"
                module.fail_json(msg=snow_error, **result)
            except Exception as detail:
                module.fail_json(msg="Unknown failure in query record: {0}".format(to_native(detail)), **result)
        module.exit_json(**result)

    # now for the real thing: (non-check mode)

    # are we creating a new record?
    if state == 'present' and number is None:
        try:
            record = conn.insert(table=table, payload=dict(data))
        except pysnow.exceptions.UnexpectedResponseFormat as e:
            snow_error = "Failed to create record: {0}, details: {1}".format(e.error_summary, e.error_details)
            module.fail_json(msg=snow_error, **result)
        except pysnow.legacy_exceptions.UnexpectedResponse as e:
            module.fail_json(msg="Failed to create record due to %s" % to_native(e), **result)
        result['record'] = record
        result['changed'] = True

    # we are deleting a record
    elif state == 'absent':
        try:
            record = conn.query(table=table, query={lookup_field: number})
            res = record.delete()
        except pysnow.exceptions.NoResults:
            res = dict(Success=True)
        except pysnow.exceptions.MultipleResults:
            snow_error = "Multiple record match"
            module.fail_json(msg=snow_error, **result)
        except pysnow.exceptions.UnexpectedResponseFormat as e:
            snow_error = "Failed to delete record: {0}, details: {1}".format(e.error_summary, e.error_details)
            module.fail_json(msg=snow_error, **result)
        except pysnow.legacy_exceptions.UnexpectedResponse as e:
            module.fail_json(msg="Failed to delete record due to %s" % to_native(e), **result)
        except Exception as detail:
            snow_error = "Failed to delete record: {0}".format(to_native(detail))
            module.fail_json(msg=snow_error, **result)
        result['record'] = res
        result['changed'] = True

    # We want to update a record
    else:
        try:
            record = conn.query(table=table, query={lookup_field: number})
            if data is not None:
                res = record.update(dict(data))
                result['record'] = res
                result['changed'] = True
            else:
                res = record.get_one()
                result['record'] = res
            if attach is not None:
                res = record.attach(b_attach)
                result['changed'] = True
                result['attached_file'] = res

        except pysnow.exceptions.MultipleResults:
            snow_error = "Multiple record match"
            module.fail_json(msg=snow_error, **result)
        except pysnow.exceptions.NoResults:
            snow_error = "Record does not exist"
            module.fail_json(msg=snow_error, **result)
        except pysnow.exceptions.UnexpectedResponseFormat as e:
            snow_error = "Failed to update record: {0}, details: {1}".format(e.error_summary, e.error_details)
            module.fail_json(msg=snow_error, **result)
        except pysnow.legacy_exceptions.UnexpectedResponse as e:
            module.fail_json(msg="Failed to update record due to %s" % to_native(e), **result)
        except Exception as detail:
            snow_error = "Failed to update record: {0}".format(to_native(detail))
            module.fail_json(msg=snow_error, **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
