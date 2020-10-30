===========================================================
Servicenow.Servicenow "When the Levee Breaks" Release Notes
===========================================================

.. contents:: Topics

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