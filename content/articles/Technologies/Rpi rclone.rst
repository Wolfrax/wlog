Raspberry backup using rclone
*****************************

:date: 2020-01-18
:modified: 2020-01-29
:tags: Raspberry, Google Drive, rclone
:summary: A note on using rclone and Google drive

Backing up raspberries using `rclone <https://rclone.org/drive/>`_ to Google drive.

Installation of rclone
======================
Installation on **rpi1**.

Please note the **"INSTRUCTIONS Google Drive Example"** at the end of rclone installation.

.. code-block:: bash

    pi@rpi1:~ $ curl -L https://raw.github.com/pageauc/rclone4pi/master/rclone-install.sh | bash
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
      0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
    100  2508  100  2508    0     0   2328      0  0:00:01  0:00:01 --:--:--  136k
    bash ver 1.6 written by Claude Pageau
    -------------------------------------------------------------------------------
    --2020-01-18 13:20:27--  https://downloads.rclone.org/rclone-current-linux-arm.zip
    Resolving downloads.rclone.org (downloads.rclone.org)... 5.153.250.7, 2a02:24e0:8:61f9::1
    Connecting to downloads.rclone.org (downloads.rclone.org)|5.153.250.7|:443... connected.
    HTTP request sent, awaiting response... 200 OK

    ...snip...

    rclone installed at /usr/bin/rclone
    -------------------------------------------------------------------------------
                     INSTRUCTIONS Google Drive Example

    1 You will be required to have a login account on the remote storage service
      Open putty SSH login session to RPI and execute command below

      rclone config

      Follow rclone prompts. For more Details See
      https://github.com/pageauc/rclone4pi/wiki/Home
    2 At name> prompt specify a reference name  eg gdmedia
    3 At storage> prompt Enter a remote storage number from List
    4 Select Auto Config, At Link: prompt, left click
      and highlight rclone url link (do not hit enter)
    5 on computer web browser url bar right click paste and go.
    6 On computer web browser security page, Confirm access.
    7 Copy web browser access security token and paste
      into RPI SSH session rclone prompt. Enter to accept
    8 To test remote service access. Execute the following where
      gdmedia is the name you gave your remote service

      rclone ls gdmedia:/

    Example sync command make source identical to destination

    rclone sync -v /home/pi/rpi-sync gdmedia:/rpi-sync

    To upgrade

      cd rpi-sync
      ./rclone-install.sh upgrade

    For more Details See https://github.com/pageauc/rclone4pi/wiki/Home
    Bye

Configuration of rclone
=======================
A Google drive item needs to be configured for rclone, below I first remove ``google_drive`` (which where wrongly
configured at a previous session) and then recreate a new remote with the same name.

**Note**

    A ``client id`` and its associated ``client secret`` needs to be generated at Google, follow these
    `instructions <https://rclone.org/drive/#making-your-own-client-id>`_ to do this.

In my case, I needed to go to `Google APIs <https://console.developers.google.com/>`_, make sure that my project
``Viltstigen`` where selected (it is by default). Then select "Credentials" to the left on the web page. A number of
previously generated "API keys" will be visible. I selected "API Key 7", then selected the "Create Credentials" drop
down menu (blue), followed by "OAuth client ID". New page, select option "Other", type in a "Name" and click "Create".
A pop-up screen appears with "client ID" and "client Secret" visible, keep them for the script below.

Note also that I have choosen a "root_folder_id" below, following the instructions
`here <https://rclone.org/drive/#root-folder-id>`_. Essentially, using the Google Drive web interface, create a new
folder (e.g. "rpi_bck"), then move into this folder and copy the last part of the URL.

.. code-block:: bash

    pi@rpi1:~/bck $ rclone config
    Current remotes:

    Name                 Type
    ====                 ====
    google_drive         drive

    e) Edit existing remote
    n) New remote
    d) Delete remote
    r) Rename remote
    c) Copy remote
    s) Set configuration password
    q) Quit config
    e/n/d/r/c/s/q> d
    Choose a number from below, or type in an existing value
     1 > google_drive
    remote> 1
    No remotes found - make a new one
    n) New remote
    s) Set configuration password
    q) Quit config
    n/s/q> n
    name> google_drive
    Type of storage to configure.
    Enter a string value. Press Enter for the default ("").
    Choose a number from below, or type in your own value
     1 / 1Fichier
       \ "fichier"
     2 / Alias for an existing remote
       \ "alias"
     3 / Amazon Drive
       \ "amazon cloud drive"
     4 / Amazon S3 Compliant Storage Provider (AWS, Alibaba, Ceph, Digital Ocean, Dreamhost, IBM COS, Minio, etc)
       \ "s3"
     5 / Backblaze B2
       \ "b2"
     6 / Box
       \ "box"
     7 / Cache a remote
       \ "cache"
     8 / Citrix Sharefile
       \ "sharefile"
     9 / Dropbox
       \ "dropbox"
    10 / Encrypt/Decrypt a remote
       \ "crypt"
    11 / FTP Connection
       \ "ftp"
    12 / Google Cloud Storage (this is not Google Drive)
       \ "google cloud storage"
    13 / Google Drive
       \ "drive"
    14 / Google Photos
       \ "google photos"
    15 / Hubic
       \ "hubic"
    16 / JottaCloud
       \ "jottacloud"
    17 / Koofr
       \ "koofr"
    18 / Local Disk
       \ "local"
    19 / Mail.ru Cloud
       \ "mailru"
    20 / Mega
       \ "mega"
    21 / Microsoft Azure Blob Storage
       \ "azureblob"
    22 / Microsoft OneDrive
       \ "onedrive"
    23 / OpenDrive
       \ "opendrive"
    24 / Openstack Swift (Rackspace Cloud Files, Memset Memstore, OVH)
       \ "swift"
    25 / Pcloud
       \ "pcloud"
    26 / Put.io
       \ "putio"
    27 / QingCloud Object Storage
       \ "qingstor"
    28 / SSH/SFTP Connection
       \ "sftp"
    29 / Transparently chunk/split large files
       \ "chunker"
    30 / Union merges the contents of several remotes
       \ "union"
    31 / Webdav
       \ "webdav"
    32 / Yandex Disk
       \ "yandex"
    33 / http Connection
       \ "http"
    34 / premiumize.me
       \ "premiumizeme"
    Storage> 13
    ** See help for drive backend at: https://rclone.org/drive/ **

    Google Application Client Id
    Setting your own is recommended.
    See https://rclone.org/drive/#making-your-own-client-id for how to create your own.
    If you leave this blank, it will use an internal key which is low performance.
    Enter a string value. Press Enter for the default ("").
    client_id> 929026972983-ngnatjtaijm1hc18s2kg6rkcktjv4od8.apps.googleusercontent.com
    Google Application Client Secret
    Setting your own is recommended.
    Enter a string value. Press Enter for the default ("").
    client_secret> ADn... [secret]
    Scope that rclone should use when requesting access from drive.
    Enter a string value. Press Enter for the default ("").
    Choose a number from below, or type in your own value
     1 / Full access all files, excluding Application Data Folder.
       \ "drive"
     2 / Read-only access to file metadata and file contents.
       \ "drive.readonly"
       / Access to files created by rclone only.
     3 | These are visible in the drive website.
       | File authorization is revoked when the user deauthorizes the app.
       \ "drive.file"
       / Allows read and write access to the Application Data folder.
     4 | This is not visible in the drive website.
       \ "drive.appfolder"
       / Allows read-only access to file metadata but
     5 | does not allow any access to read or download file content.
       \ "drive.metadata.readonly"
    scope> 3
    ID of the root folder
    Leave blank normally.

    Fill in to access "Computers" folders (see docs), or for rclone to use
    a non root folder as its starting point.

    Note that if this is blank, the first time rclone runs it will fill it
    in with the ID of the root folder.

    Enter a string value. Press Enter for the default ("").
    root_folder_id> 1fMjA9uqc7cqphmsdW7DUhmdFQ9Ib44Ti
    Service Account Credentials JSON file path
    Leave blank normally.
    Needed only if you want use SA instead of interactive login.
    Enter a string value. Press Enter for the default ("").
    service_account_file>
    Edit advanced config? (y/n)
    y) Yes
    n) No
    y/n> n
    Remote config
    Use auto config?
     * Say Y if not sure
     * Say N if you are working on a remote or headless machine
    y) Yes
    n) No
    y/n> n
    If your browser doesn't open automatically go to the following link: https://accounts.google.com/o/oauth2/auth?access_type=offline&client_id=929026972983-ngnatjtaijm1hc18s2kg6rkcktjv4od8.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.file&state=zNJXAabBYq3h47mRFBBDPQ
    Log in and authorize rclone for access
    Enter verification code> 4/vgFZnvkQPNbnaZsTLaUsrylS7feY0vhiJIFIuT19GzQl9pAQd9oCeag
    Configure this as a team drive?
    y) Yes
    n) No
    y/n> n
    --------------------
    [google_drive]
    type = drive
    client_id = 929026972983-ngnatjtaijm1hc18s2kg6rkcktjv4od8.apps.googleusercontent.com
    client_secret = ADnKctAeKLK-BUrRiimgg4Np
    scope = drive.file
    root_folder_id = 1fMjA9uqc7cqphmsdW7DUhmdFQ9Ib44Ti
    token = {"access_token":"ya29.Il-6B94wEV6RU36hajNWRva4xAUWO_FoUfOBGI3iWAMyPRZr5ZIFO9sadE-oBksypv5vWVEUVNSQDIvPFX1TriqfGgjtdOlEG102-1mAeTfALnBUuOhtZ7rqpff4dXOPsg","token_type":"Bearer","refresh_token":"1//0c_Fz_obvU3LpCgYIARAAGAwSNwF-L9IrWuIw7flrX2ggHHLPNoS2PL7vALudrrE1NYJmIghUfeRoIUXg9qyINwRAcf62Ps7yGoo","expiry":"2020-01-18T17:09:31.820516378+01:00"}
    --------------------
    y) Yes this is OK
    e) Edit this remote
    d) Delete this remote
    y/e/d> y
    Current remotes:

    Name                 Type
    ====                 ====
    google_drive         drive

    e) Edit existing remote
    n) New remote
    d) Delete remote
    r) Rename remote
    c) Copy remote
    s) Set configuration password
    q) Quit config
    e/n/d/r/c/s/q> q

Now try rclone by copying a file (e.g. "backup.log") to "google_drive" and create a new folder "rpi1". Then list
content in "google_drive", folder "rpi" to verify that the file is there. Finally list folders visible in "google_drive".

.. code-block:: bash

    pi@rpi1:~/bck $ rclone copy backup.log google_drive:rpi1
    pi@rpi1:~/bck $ rclone ls google_drive:rpi1
      1104214 backup.log
    pi@rpi1:~/bck $ rclone lsd google_drive:
              -1 2020-01-18 16:10:44        -1 rpi1

Backup
======
Now ``rclone`` can be used to backup files to Google Drive.

rpi1 backup
-----------
**rpi1** have an additional USB memory installed. Production data is stored in Mongo database.

Plug the USB memory into a USB port and it should be automatically mounted by the raspberry on ``/dev/sda*``,
for example ``/dev/sda1``.

To check availability do

.. code-block:: bash

    $ sudo lsblk -f

    NAME        FSTYPE LABEL    UUID                                 MOUNTPOINT
    sda
    └─sda1      vfat            8F3F-8E75                            /media/pi/8F3F-8E75
    mmcblk0
    ├─mmcblk0p1 vfat   RECOVERY 6363-3634
    ├─mmcblk0p2
    ├─mmcblk0p5 ext4   SETTINGS 444485b7-f8cb-4f4c-8b9a-6fedf94efed1 /media/pi/SETTINGS
    ├─mmcblk0p6 vfat   boot     0181-4B93                            /boot
    └─mmcblk0p7 ext4   root     65b49769-3b56-43b9-b037-bf4a8da3a41a /

Note the mount point for the USB memory stick ``/media/pi/8F3F-8E75``, make a softlink for more convenient access,
for example ``$ ln -s /media/pi/8F3F-8E75/ /home/pi/bck/``.

If needed format the USB memory stick through ``$ sudo mkfs.vfat /dev/sda1 -n untitled``.
If the mkfs.vfat command is not available install "dosfstools" first through ``$ sudo apt-get install dosfstools``.

Now add the following content into a file named backup.sh:

.. code-block:: bash

    #!/usr/bin/env bash
    #
    # Daily backup from /etc/crontab
    #
    # Adopted from <https://help.ubuntu.com/lts/serverguide/backup-shellscripts.html>
    # and <http://www.tldp.org/LDP/solrhe/Securing-  Optimizing-Linux-RH-Edition-v1.3/chap29sec306.html>
    #
    # To list: tar -tzvf /home/pi/bck/host-Monday.tgz
    # To restore: tar -xzvf /home/pi/bck/host-Monday.tgz -C /tmp etc/hosts (restore /etc/hosts file to /etc/tmp/hosts)
    # Notice the leading "/" is left off the path of the file to restore.
    # To restore all (overwrites everything):
    #   cd
    #   sudo tar -xzvf /home/pi/bck/host-Monday.tgz

    # What to backup
    backup_files="/home/pi/.ssh /home/pi/app"

    # Where to backup to.
    # Note, this is a softlinked directory to /media/pi/8F3F-8E75/bck which resides on a separate USB  flash memory
    dest="/home/pi/bck"

    # Create archive filename.
    day=$(date +%A)
    hostname=$(hostname -s)
    archive_file="$hostname-$day.tgz"

    # Print start status message.
    echo "-----"
    echo "Backing up $backup_files to $dest/$archive_file"
    date
    echo

    # Backup the files using tar.
    tar czf $dest/$archive_file $backup_files

    # Print end status message.
    echo
    echo "Backup finished"
    date

    # Long listing of files in $dest to check file sizes.
    ls -lh $dest/
    echo "-----"

Then do ``$ chmod a+x backup.sh``, the script is executed through user crontab (not /etc/crontab) by inserting this line

.. code-block:: bash

    00 2    * * *   sh /home/pi/rpi1/app/RPiscripts/backup.sh >> /home/pi/bck/backup.log 2>&1

Thus, by 2:00am the script is executed. Note that the folder ``home/pi/app`` is included although no production data
is there. I then upload to Google Drive by this line in the same crontab at 4:00am.

.. code-block:: bash

    00 4    * * *   rclone sync /home/pi/bck/ google_drive:rpi1

rpi3 backup
-----------
For **rpi3** I have 2 files that is of "production type", ie generated by a program. These are synched to Google Drive
once per hour from crontab entries

.. code-block:: bash

    0 * * * * rclone sync /home/pi/app/spots/radar/spots_stats.json google_drive:spots
    0 * * * * rclone sync /home/pi/app/spots/radar/spots_stats.json.1 google_drive:spots

**Note**

    When google_drive is setup when installing rclone on **rpi3**, the root is different compared to **rpi1**.
    For **rpi3** it points to ``rpi_bck/rpi3`` on Google Drive, while for **rpi1** it points to ```rpi_bck``.
    Thus, for **rpi1** an additional suffix is needed to store files at ``rpi_bck/rpi1`` by using ``google_drive:rpi1``
    in rclone commands on **rpi1** compared to **rpi3**.
