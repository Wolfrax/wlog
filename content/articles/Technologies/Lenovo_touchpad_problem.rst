Lenovo Touchpad problem
***********************

:date: 2020-02-01
:modified: 2020-02-01
:tags: Linux, Mint, Lenovo

Using a Lenovo Thinkpad T440 with Linux Mint (4.15.0-70-generic) I have a problem with 2-finger scrolling using the
touchpad. It stopped working after suspend/resume. This is a known problem affecting other models also.

Manually this can be fixes as so

.. code-block:: bash

    $ sudo modprobe -r psmouse # Unload the psmouse driver
    $ sudo modprobe psmouse # then reload it again

To make this permanent update the with a kernel parameter. Edit **/etc/default/grub**, change the following line, from

.. code-block:: bash

    GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"

to

.. code-block:: bash

    GRUB_CMDLINE_LINUX_DEFAULT="quiet splash psmouse.synaptics_intertouch=0"

Then regenerate the **grub.cfg** file by

.. code-block:: bash

    $ sudo grub-mkconfig -o /boot/grub/grub.cfg

Problem should be fixed.

You can try the kernel parameter before editing the **grub** file by entering the **grub** bootloader before booting the
kernel. Restart the computer and press repeatedly **esc**-key during boot-up. Edit the line starting with **linux** and
add **psmouse.synaptics_intertouch=0** at the end. Press **ctrl-x** to load the kernel with this parameter setting.
Of course, next time there is a restart the parameter setting is not there. Hence, to make it permanent edit the **grub**
-file as above.