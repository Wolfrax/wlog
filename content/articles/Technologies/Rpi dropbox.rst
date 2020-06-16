Raspberry backup using dropbox
******************************

:date: 2020-01-25
:modified: 2020-01-25
:tags: Raspberry, Dropbox

Follow the recipe <https://www.raspberrypi.org/magpi/dropbox-raspberry-pi/>
In Dropbox, create a new app (find the "..." in the right hand corner, selected Developer and Create App), choose
Dropbox API (not business), select specific folder or full usage (I choose specific folder) and an app name, in my
case WolfraxRPiBck (it has to be unique wihtin DropBox community). Click on "Generate access token" and copy the
resulting key.

.. code-block:: bash

    $ git clone https://github.com/andreafabrizi/Dropbox-Uploader.git
    $ cd Dropbox-Uploader/
    $ chmod a+x ./dropbox_uploader.sh
    $ ./dropbox_uploader.sh
     This is the first time you run this script, please follow the instructions:

     1) Open the following URL in your Browser, and log in using your account: https://www.dropbox.com/developers/apps
     2) Click on "Create App", then select "Dropbox API app"
     3) Now go on with the configuration, choosing the app permissions and access restrictions to your DropBox folder
     4) Enter the "App Name" that you prefer (e.g. MyUploader4177213067640)

     Now, click on the "Create App" button.

     When your new App is successfully created, please click on the Generate button
     under the 'Generated access token' section, then copy and paste the new access token here:

     # Access token: QzVDx[...]

     > The access token is QzVDx[...] Looks ok? [y/N]: y
       The configuration has been saved.
     $ ./dropbox_uploader.sh info
    Dropbox Uploader v1.0

     > Getting info...

    Name:		Mats Melander
    UID:		dbid:AAC...
    Email:		mats.m...
    Country:	SE

    $ ./dropbox_uploader.sh upload README.md /
     > Uploading "/home/pi/app/Dropbox-Uploader/README.md" to "/README.md"...
    ######################################################################## 100.0%
    DONE

Edit the `dropbox_uploader.sh` file and change `SHOW_PROGRESSBAR = 0` to `SHOW_PROGRESSBAR = 1`
The script is ready to be used.

.. code-block:: bash

    00 3    * * 0   sh /home/pi/rpi1/app/RPiscripts/backup_dropbox.sh -f /home/pi/.dropbox_uploader >> /home/pi/backup_dropbox.log 2>&1

Once per week at 3:00pm upload to dropbox, the ``backup_dropbox.sh`` is

.. code-block:: bash

    #!/usr/bin/env bash
    #
    # Daily upload to Dropbox of backup files
    #
    # Copy everything in the /home/pi/bck/ directory to Dropbox and make a listing
    # This script is dependent on the backup.sh script
    #

    echo "-----"
    echo "Uploading to Dropbox of backup files"
    date
    echo

    /home/pi/app/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/bck/* /RPi1_backup/
    /home/pi/app/Dropbox-Uploader/dropbox_uploader.sh list /RPi1_backup/

    echo
    echo "Upload finished finished"
    date
    echo "-----"

The file ``.dropbox_uploader`` is one row with the access token for Dropbox.

.. code-block:: bash

    OAUTH_ACCESS_TOKEN=QzV[...]