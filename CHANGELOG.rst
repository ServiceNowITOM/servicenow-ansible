===================================
Servicenow.Servicenow Release Notes
===================================

.. contents:: Topics


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
