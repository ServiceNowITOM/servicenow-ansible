snow_record_find - Search for multiple records from ServiceNow
====================================
- [Synopsis](Synopsis)
- [Requirements](Requirements)
- [Parameters](Parameters)
- [Examples](Examples)

## Synopsis
- Gets multiple records from a specified table from ServiceNow based on a query dictionary.

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
<td><b>table</b></br>
</td>
<td><b>Default:</b><br> 
incident</td>
<td></td>
<td>  Table to query for records.  </td>
</tr>
<tr>
<td><b>max_records</b></br>
</td>
<td><b>Default:</b><br> 
20</td>
<td></td>
<td>  Maximum number of records to return.  </td>
</tr>
<tr>
<td><b>return_fields</b></br>
</td>
<td></td>
<td></td>
<td>  Fields of the record to return in the json.  By default, all fields will be returned.  </td>
</tr>
<tr>
<td><b>order_by</b></br>
</td>
<td><b>Default:</b><br> 
-created_on</td>
<td></td>
<td>  Field to sort the results on.  Can prefix with "-" or "+" to change descending or ascending sort order.  </td>
</tr>
<tr>
<td><b>query</b></br>
<p style="color:red;font-size:75%">required</p></td>
<td></td>
<td></td>
<td>  Dict to query for records.  </td>
</tr>
</table>

## Examples
```

- name: Search for incident assigned to group, return specific fields
  snow_record_find:
    username: ansible_test
    password: my_password
    instance: dev99999
    table: incident
    query:
      assignment_group: d625dccec0a8016700a222a0f7900d06
    return_fields:
      - number
      - opened_at

- name: Search for incident using host instead of instance
  snow_record_find:
    username: ansible_test
    password: my_password
    host: dev99999.mycustom.domain.com
    table: incident
    query:
      assignment_group: d625dccec0a8016700a222a0f7900d06
    return_fields:
      - number
      - opened_at

- name: Using OAuth, search for incident assigned to group, return specific fields
  snow_record_find:
    username: ansible_test
    password: my_password
    client_id: "1234567890abcdef1234567890abcdef"
    client_secret: "Password1!"
    instance: dev99999
    table: incident
    query:
      assignment_group: d625dccec0a8016700a222a0f7900d06
    return_fields:
      - number
      - opened_at

- name: Find open standard changes with my template
  snow_record_find:
    username: ansible_test
    password: my_password
    instance: dev99999
    table: change_request
    query:
      AND:
        equals:
          active: "True"
          type: "standard"
          u_change_stage: "80"
        contains:
          u_template: "MY-Template"
    return_fields:
      - sys_id
      - number
      - sys_created_on
      - sys_updated_on
      - u_template
      - active
      - type
      - u_change_stage
      - sys_created_by
      - description
      - short_description

```