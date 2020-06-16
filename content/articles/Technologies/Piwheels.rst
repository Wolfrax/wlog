Piwheels
********

:date: 2020-02-02
:modified: 2020-02-02
:tags: Python

A note on piwheels.

The PyPi (Python Package Index) is the package repository for Python modules. **$ pip install** scouts this repository
when installing modules. Some of the modules have been implemented in C, and thus require compilation for the specific
target installation. This takes time (and might fail).

The general solution to this is Python wheels, which includes pre-build binaries for Windows, macOS and Linux
(32/64 bits). However, Arm is not included and Raspberry is build on Arm. Enter piwheels.

This repository provides Arm platform wheels, ie pre-compiled binary Python packages. Suitable for Raspberry Pi.

For Raspberry Pi running Raspbian Stretch, this is by default enabled for Pip. For older versions (e.g. Jessie) this
should be included in **/etc/pip.conf**

.. code-block:: bash

    [global]
    extra-index-url=https://www.piwheels.org/simple

For Raspbian Jessie: Upgrade pip to >=9.0.1 using **$ sudo pip3 install pip --upgrade**.