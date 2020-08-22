snow_record - Manage records in ServiceNow
====================================
- [Synopsis](Synopsis)
- [Requirements](Requirements)
- [Parameters](Parameters)
- [Examples](Examples)

## Synopsis
- Creates, deletes and updates a single record in ServiceNow.

## Requirements
- python pysnow (pysnow)

## Parameters

<table>
<tr>
<th> Parameter </th>
<th> Choices/Defaults </th>
<th> Configuration </th>
<th> Comments </th>
</tr>
<tr>
<td><b>number</b></br>
</td>
<td></td>
<td></td>
<td>  Record number to update.  Required for C(state:absent).  </td>
</tr>
<tr>
<td><b>state</b></br>
<p style="color:red;font-size:75%">required</p></td>
<td><b>Choices:</b><br>
- present
- absent
</td>
<td></td>
<td>  If C(present) is supplied with a C(number) argument, the module will attempt to update the record with the supplied data.  If no such record exists, a new one will be created.  C(absent) will delete a record.  </td>
</tr>
<tr>
<td><b>attachment</b></br>
</td>
<td></td>
<td></td>
<td>  Attach a file to the record.  </td>
</tr>
<tr>
<td><b>table</b></br>
</td>
<td><b>Default:</b><br> 
incident</td>
<td></td>
<td>  Table to query for records.  </td>
</tr>
<tr>
<td><b>lookup_field</b></br>
</td>
<td><b>Default:</b><br> 
number</td>
<td></td>
<td>  Changes the field that C(number) uses to find records.  </td>
</tr>
<tr>
<td><b>data</b></br>
</td>
<td></td>
<td></td>
<td>  key, value pairs of data to load into the record. See Examples.  Required for C(state:present).  </td>
</tr>
</table>

## Examples
```

- name: Grab a user record
  snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: present
    number: 62826bf03710200044e0bfc8bcbe5df1
    table: sys_user
    lookup_field: sys_id

- name: Grab a user record using OAuth
  snow_record:
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
  snow_record:
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
  snow_record:
    username: ansible_test
    password: my_password
    host: dev99999.mycustom.domain.com
    state: present
    data:
      short_description: "This is a test incident opened by Ansible"
      priority: 2

- name: Delete the record we just made
  snow_record:
    username: admin
    password: xxxxxxx
    instance: dev99999
    state: absent
    number: "{{new_incident['record']['number']}}"

- name: Delete a non-existant record
  snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: absent
    number: 9872354
  failed_when: false

- name: Update an incident
  snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: present
    number: INC0000055
    data:
      work_notes : "Been working all day on this thing."

- name: Attach a file to an incident
  snow_record:
    username: ansible_test
    password: my_password
    instance: dev99999
    state: present
    number: INC0000055
    attachment: README.md
  tags: attach

```