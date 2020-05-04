Role Name
=========

Install and configure ServiceNow MID (Management, Instrumentation, & Discovery) server instances.

Requirements
------------

Server must be provisioned to meet the Service Now [Mid Server Requirements](https://docs.servicenow.com/bundle/orlando-servicenow-platform/page/product/mid-server/reference/r_MIDServerSystemRequirements.html)


Role Variables
--------------

| Name | Defaults | Comments |
|------|----------|----------|
| now_instance | ENV: SN_INSTANCE | name of ServiceNow instance. *required |
| now_instance_username |  ENV: SN_USERNAME | Username used to register mid server with ServiceNow instance |
| now_instance_password | ENV: SN_PASSWORD | Password used to register mid server with ServiceNow instance |
| now_mid_name | `ansible_hostname` | Name used to register mid server |
| now_mid_threads | 25 | Controls the number of execution threads (simultaneous work) that may be used by probes |
| now_mid_date_format | 'yyyy-MM-dd HH:mm:ss' | Format of date and time |
| now_mid_proxy | false | Is a proxy server used BOTH for contacting your Service-now instance AND for downloading upgrades. |
| now_mid_proxy_host | 'YOUR_PROXY_HOST' | Proxy host address |
| now_mid_proxy_port | 'YOUR_PROXY_PORT' | Proxy port number |
| now_mid_proxy_username | 'YOUR_PROXY_USER_NAME' | Proxy server username |
| now_mid_proxy_password | 'YOUR_PROXY_PASSWORD' | Proxy server password |


Example Playbook
----------------

```
    - hosts: mid
      become: yes

      tasks:
      - include_role:
          name: servicenow.servicenow.midserver
```

License
-------

MIT

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
