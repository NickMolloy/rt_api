
==================================
Welcome to rt_api's documentation!
==================================

rt_api is a python client for the Rooster Teeth Api. It allows easy access to resources such as episodes, seasons, shows, and users.

It supports Python 2.6, 2.7, 3.3, 3.4, 3.5, 3.6, and 3.7

Quickstart
==========

.. _installation-guide:

Installation
------------

To install rt_api, run:

.. code::

    pip install rt_api

Alternatively rt_api can be installed from source by cloning the repository
and running setuptools:

.. code::

    git clone https://github.com/NickMolloy/rt_api
    cd rt_api
    python setup.py install



Using rt_api
---------------

The main entry point for the library is the :class:`~rt_api.api.Api` class.
Instantiating this class will give access to all of the API functionality.
For example:

.. code-block:: python

   from rt_api.api import Api

   api = Api()  # Instantiate api. Generates default access token.
   latest_episodes = api.episodes()  # Get a list of the latest episodes
   newest_episode = latest_episodes[0]
   print(newest_episode.title)  # Print out episode title
   show = newest_episode.show  # Get a reference to the show the episode is from
   print(show.name)  # Print out name of the show

If you want to be able to perform actions as a specific user, you must first
authenticate:

.. code-block:: python

   from rt_api.api import Api

   api = Api()
   api.authenticate("myUsername", "myPassword")  # Authenticate as myUsername

From this point, all actions performed will be done in the context of that user.
For instance, the current user is available through the ``me`` attribute of the api:

.. code-block:: python

    my_user = api.me  # Get the user object associated with the authenticated user
    my_user.queue  # Get the current user's episode watch list


For more information on the available actions, see the :ref:`package documentation <package-doc>`,
or some :ref:`examples <examples>`.


Codebase Overview
-----------------
:mod:`rt_api.api` contains the api itself, which actually performs the api actions.

:mod:`rt_api.models` contains the models of the api.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
