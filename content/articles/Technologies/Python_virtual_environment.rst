Python virtual environment
**************************

:date: 2020-02-02
:modified: 2020-02-02
:tags: Python


I use Python **virtualenv**, **virtualenvwrapper** and **autoenv**.

Installation

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install python-setuptools
    $ sudo easy_install pip
    $ sudo pip install virtualenv
    $ sudo pip install virtualenvwrapper
    $ sudo pip install autoenv

My virtualenv root is at **~/.virtualenvs**, so update **~/.bashrc** accordingly

.. code-block:: bash

    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/app
    source /usr/local/bin/virtualenvwrapper.sh
    source /usr/local/bin/activate.sh

Then create an **.env** file in the folder were the project root is located (for example "Traffic" is used below) with
this content **"workon Traffic"**.

Do **"$ mkvirtualenv Traffic"**. When changing directory (cd) into the folder were the **.env**-file is located
**autoenv** will automatically trigger the virtualenv.

To use Python3, use this command **"$ mkvirtualenv --python=/usr/bin/python3 Traffic"**. To find the path to Python3,
use **"$ which python3""**.

If autoenv is not used, activate the virtualenv by **"$ workon Traffic"**, deactivate by **"$ deactivate"**.
After activating the virtualenv, install packages by (Traffic) **"$ pip install requests"**
(for Python3 do **"(Traffic) $ pip3 install requests"**).

Refer to documentation `here <https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html>`__.