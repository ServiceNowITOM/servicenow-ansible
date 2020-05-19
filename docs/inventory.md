servicenow.servicenow.now - ServiceNow Inventory Plugin
====================================
- [Synopsis](Synopsis)
- [Requirements](Requirements)
- [Parameters](Parameters)
- [Examples](Examples)

## Synopsis
- ServiceNow Inventory plugin

## Requirements
- requests
- netaddr

## Parameters

<table>
<tr>
<th> Parameter </th>
<th> Choices/Defaults </th>
<th> Configuration </th>
<th> Comments </th>
</tr>
<tr>
<td><b>username</b></br>
<p style="color:red;font-size:75%">required</p></td>
<td></td>
<td><b>env:</b><br>
-   name: SN_USERNAME
</td>
<td> The ServiceNow user acount, it should have rights to read cmdb_ci_server (default), or table specified by SN_TABLE</td>
</tr>
<tr>
<td><b>plugin</b></br>
<p style="color:red;font-size:75%">required</p></td>
<td><b>Choices:</b><br>
- servicenow.servicenow.now
</td>
<td></td>
<td> The name of the ServiceNow Inventory Plugin, this should always be 'servicenow.servicenow.now'.</td>
</tr>
<tr>
<td><b>fields</b></br>
</td>
<td><b>Default:</b><br> 
ip_address,fqdn,host_name,sys_class_name,name</td>
<td></td>
<td> Comma seperated string providing additional table columns to add as host vars to each inventory host.</td>
</tr>
<tr>
<td><b>instance</b></br>
<p style="color:red;font-size:75%">required</p></td>
<td></td>
<td><b>env:</b><br>
-   name: SN_INSTANCE
</td>
<td> The ServiceNow instance URI. The URI should be the fully-qualified domain name, e.g. 'your-instance.servicenow.com'.</td>
</tr>
<tr>
<td><b>filter_results</b></br>
</td>
<td><b>Default:</b><br> 
</td>
<td></td>
<td> Filter results with sysparm_query encoded query string syntax. Complete list of operators available for filters and queries.</td>
</tr>
<tr>
<td><b>proxy</b></br>
</td>
<td><b>Default:</b><br> 
</td>
<td></td>
<td> Proxy server to use for requests to ServiceNow.</td>
</tr>
<tr>
<td><b>enhanced</b></br>
</td>
<td><b>Default:</b><br> 
False</td>
<td></td>
<td> enable enhanced inventory which provides relationship information from CMDB. Requires installation of Update Set.</td>
</tr>
<tr>
<td><b>selection_order</b></br>
</td>
<td><b>Default:</b><br> 
ip_address,fqdn,host_name,name</td>
<td></td>
<td> Comma seperated string providing ability to define selection preference order.</td>
</tr>
<tr>
<td><b>table</b></br>
</td>
<td><b>Default:</b><br> 
cmdb_ci_server</td>
<td></td>
<td> The ServiceNow table to query</td>
</tr>
<tr>
<td><b>enhanced_groups</b></br>
</td>
<td><b>Default:</b><br> 
True</td>
<td></td>
<td> enable enhanced groups from CMDB relationships. Only used if enhanced is enabled.</td>
</tr>
<tr>
<td><b>password</b></br>
</td>
<td></td>
<td><b>env:</b><br>
-   name: SN_PASSWORD
</td>
<td> The ServiceNow instance user password.</td>
</tr>
</table>

## Examples
```

plugin: servicenow.servicenow.now
instance: demo.service-now.com
username: admin
password: password
keyed_groups:
  - key: sn_sys_class_name | lower
    prefix: ''
    separator: ''

plugin: servicenow.servicenow.now
instance: demo.service-now.com
username: admin
password: password
fields: [name,host_name,fqdn,ip_address,sys_class_name, install_status, classification,vendor]
keyed_groups:
  - key: sn_classification | lower
    prefix: 'env'
  - key: sn_vendor | lower
    prefix: ''
    separator: ''
  - key: sn_sys_class_name | lower
    prefix: ''
    separator: ''
  - key: sn_install_status | lower
    prefix: 'status'

plugin: servicenow.servicenow.now
instance: demo.service-now.com
username: admin
password: password
fields:
  - name
  - sys_tags
compose:
  sn_tags: sn_sys_tags.replace(" ", "").split(',')
  ansible_host: sn_ip_address
keyed_groups:
  - key: sn_tags | lower
    prefix: 'tag'

```