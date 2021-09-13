===================================
Servicenow.Servicenow Release Notes
===================================

.. contents:: Topics


v1.0.7
======

Release Summary
---------------

DEPRECATED - This collection is deprecated in favor of servicenow.itsm.

Minor Changes
-------------

- add environment var SN_FILTER_RESULTS to inventory plugin

v1.0.6
======

Bugfixes
--------

- makes auth backwards compatible by defaulting to OAuth if client_id is present without specifying auth
- order_by again working by locally sorting return list of records

v1.0.5
======

Major Changes
-------------

- refactored client to inherit from AnsibleModule
- supports OpenID Connect authentication protocol
- supports bearer tokens for authentication

Minor Changes
-------------

- standardized invocation output

Breaking Changes / Porting Guide
--------------------------------

- auth field now required for anything other than Basic authentication

v1.0.4
======

Major Changes
-------------

- add new tests (find with no result, search many)
- add related tests
- add support for ServiceNOW table api display_value exclude_reference_link and suppress_pagination_header
- use new API for pysnow >=0.6.0

v1.0.3
======

Release Summary
---------------

use consistent auth parameters across plugins and modules

Minor Changes
-------------

- adds the ability to use `SN_INSTANCE` (ex. `dev61775`) or `SN_HOST` (ex. `dev61775.service-now.com`) with the inventory plugin.

Bugfixes
--------

- fix inventory plugin transforming hostnames unnecessarily
- fix malformed documentation on docs.ansible.com
