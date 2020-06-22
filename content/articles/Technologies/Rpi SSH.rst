SSH
***

:date: 2020-01-11
:modified: 2020-06-22
:tags: Raspberry, SSH
:summary: A note on using SSH

This describes how to connect with `SSH <https://en.wikipedia.org/wiki/Secure_Shell>`_

To not provide password manually a public/private keys can be generated and stored at appropriate directories in host
(private key) and target (public key).

To generate keys on my host (Linux or MacBook) and then store the public key on the raspberry host ``rpi1`` do

.. code-block:: bash

    $ ssh-keygen -t rsa -C pi@rpi1
    $ cat ~/.ssh/id_rsa.pub | ssh pi@rpi1.local 'cat >> .ssh/authorized_keys'

Note that the last command transfer the public key to rpi1 using ssh and store it in file ``~/.ssh/authorized_keys``.
This will invoke to provide password for SSH.

Make sure that directory ``.ssh`` exists on home directory for user pi at the raspberry host rpi1.
If not do ``$ install -d -m 700 ~/.ssh`` at the rpi1 first

Note, if file ``~/.ssh/id_rsa.pub`` already exists at host there is no need to do ssh-keygen, simply do the last
command above ($ cat ~/.ssh...).

To remove an entry in ``~/.ssh/known_hosts`` do

.. code-block:: bash

    $ ssh-keygen -R rpi1.local

See `SSH passwordless <https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md>`_.

If ssh tries to connect to a known IP address but receives a different ssh key compared to the one it got before,
it makes sense to treat this as a possible security problem and refuse to connect. This can happen if there is a new
installation of Raspbian and most commonly manifests by the ssh client reporting something like:

.. code-block:: bash

    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
    Someone could be eavesdropping on you right now (man-in-the-middle attack)!
    It is also possible that a host key has just been changed.
    The fingerprint for the ECDSA key sent by the remote host is
    ...

To mitigate this the local ssh client file ``known_hosts`` needs to be updated. Do this locally assuming the
issues occur while using ssh vs host 192.168.1.50 (rpi1.local).

.. code-block:: bash

    $ ssh-keyscan 192.168.1.50 >> ~/.ssh/known_hosts

If the IP address or the node name (e.g. "192.168.1.50" or "rpi1.local") has been used before, an error message might
occur. To find out which entry is for a known hostname in known_hosts:

.. code-block:: bash

    $ ssh-keygen -H  -F <hostname or IP address>

To delete a single entry from known_hosts (remove both IP address and node name as needed):

.. code-block:: bash

    $ ssh-keygen -R <hostname or IP address>

Then re-do the command `$ ssh-keyscan 192.168.1.50 >> ~/.ssh/known_hosts`.

Github ssh access
=================

On Raspberry Pi do (see https://help.github.com/articles/generating-ssh-keys/)

.. code-block:: bash

    $ ssh-keygen -t rsa -b 4096 -C "mats.melander@gmail.com" # Generate public/private rsa keys in ~/.ssh directory
    $ eval "$(ssh-agent -s)"                                 # Make sure ssh is running, should respond "Agent pid 12693"
    $ ssh-add ~/.ssh/id_rsa
    $ cat .ssh/id_rsa.pub                                    # List content, copy the content

Go to github and login, under settings/SSH keys, do "add new key". Copy content from the public key.

Verify on RPi with

.. code-block:: bash

    $ ssh -T git@github.com
    Warning: Permanently added the RSA host key for IP address '192.30.252.128' to the list of known hosts.
    Hi Wolfrax! You've successfully authenticated, but GitHub does not provide shell access.

To have github working with ssh rather than https do (see `<https://help.github.com/articles/changing-a-remote-s-url/>`_,
below is valid for user Wolfrax and repository "Swind")

.. code-block:: bash

    $ git remote -v
    origin\	https://github.com/Wolfrax/Swind.git (fetch)
    origin\	https://github.com/Wolfrax/Swind.git (push)
    $ git remote set-url origin git@github.com:Wolfrax/Swind.git
    $ git remote -v
    origin\	git@github.com:Wolfrax/Swind.git (fetch)
    origin\	git@github.com:Wolfrax/Swind.git (push)

OSX
===
On Mac OSX, I made the following update to ``~/.ssh/config`` (user config file, the system wide file is on
/etc/ssh/ssh_config, or equivalently /private/etc/ssh/ssh_config).

.. code-block:: bash

    AddressFamily inet

This forces ssh to use IPv4 only, default value is "any" which enables both IPv4 and IPv6. I had some trouble with
one Raspberry (rpi2, 192.168.1.51) when using ``$ ssh pi@rpi2.local``. When debugging (using ``$ ssh -vvv pi@rpi2.local
``) it turned out that ``rpi2.local`` were translated into an IPv6 address instead of an IPv4
for unknown reasons. Using an IPv6, ssh command had to timeout then it retried with a correct IPv4 address instead and
connected successfully. This caused and a long connection time.

For my other raspberries, this has not been a problem. I have not digged further into why this became a problem for
**rpi2** only.