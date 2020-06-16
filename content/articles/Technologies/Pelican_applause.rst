Pelican applause button
***********************

:date: 2020-02-12
:modified: 2020-02-12
:tags: Blog, Pelican

For blog entries, the `applause button <https://applause-button.com/>`__ have been enabled in **pelicanconf.py** with
this row

.. code-block:: bash

    APPLAUSE_BUTTON = True

The number of claps is made persistent  by a cloud-based sever with a REST API, see the link above.
I don't expect a lot (read any) claps on the blog posts, but I still wanted to create a simple page with a table that
list blog post name and the number of claps. To do this the **get-multiple** method is used in a simple Python script.

The script walks a directory structure using **os.walk**-function returning 3 parameters. If the second (**dirs**)
parameter is empty we are in a "leaf"-directory and I take the value of the first parameter (**root**) to construct
a JSON array used as an argument to **get-multiple**.

**get-multiple** has a restriction that maximum 100 URLs can be added to the JSON array. Hence, I need to cater for this.
Once I have this array, I use the **requests** Python library to POST the array to
**https://api.applause-button.com/get-multiple**, then I parse the result (if I get a status code that indicate success).

At the end, I use `Flask <https://flask.palletsprojects.com/en/1.1.x/>`__ and a template to generate an HTML page
with the desired result. The **Flask** application is using `gunicorn <https://gunicorn.org/>`__ listening on port 8098
at my local raspberry (**rpi2**), hence UFW needs to be configured to have the port open.

More details and source code `here <https://github.com/Wolfrax/claps>`__
