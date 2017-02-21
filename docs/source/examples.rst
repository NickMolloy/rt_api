.. _examples:

=============
Example Usage
=============

.. code-block:: python

    from rt_api.api import Api
    import itertools

    # Instantiate Api
    api = Api()
    # Get an iterator for the episode feed for Achievement Hunter
    episode_feed = api.episodes(site="AchievementHunter")
    # Slice first 5 episodes from feed into a list
    latest_episodes = list(itertools.islice(episode_feed, 4))
    # Iterate over these latest episodes
    for episode in latest_episodes:
        print("{0} - {1}".format(episode.show_name, episode.title))
        print("\t{0} seconds long".format(episode.length))
        if episode.is_sponsor_only:
            print("\tIs only available to sponsors")

    # Sign in as a user
    api.authenticate("someUsername", "somePassword")
    # Add episode to our queue
    episode = latest_episodes[0]
    episode.add_to_queue()
    # Get a reference to our user
    me = api.me
    print("My username is {0}, my name is {1}".format(me.username, me.name))
    print("I {0} a sponsor".format("am" if me.is_sponsor else "am not"))
    # Change our name
    me.name = "New Name"
    me.update()
    print("Now my name is {0}".format(me.name))


---------
Iterables
---------
Some methods of :class:`~rt_api.api.Api` return an iterable collection of a resource
e.g :meth:`~rt_api.api.Api.episodes`, :meth:`~rt_api.api.Api.shows`,
and :meth:`~rt_api.api.Api.user_queue`.
The iterable returned starts at the specified page, and can be used to
retrieve all items onwards.

For example, if ``page`` is set to 2 then the iterable returned will allow iteration
over all items from item 21 onwards (The default value of ``count`` is 20).

Example::

    from rt_api.api import Api

    api = Api()
    show_feed = api.shows(page=5)
    # Can iterate over all shows, starting at the 81st item from the feed
    for show in show feed:
        # Do something with show
        pass
