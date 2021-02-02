===========================================================
Servicenow.Servicenow "When the Levee Breaks" Release Notes
===========================================================

.. contents:: Topics


v1.0.4
======

Release Summary
---------------

Bugfixes
--------
Fixes #34
Fixes #35

Minor Changes
-------------

Use new PySnow API interface (0.6.0 - 0.7.X)

Add support for parameters (https://developer.servicenow.com/dev.do#!/reference/api/paris/rest/c_TableAPI#table-GET):
- display_value
- exclude_reference_link
- suppress_pagination_header

New tests:
- search many
- search with no result
- search with display_value/exclude_reference_link

=======


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

