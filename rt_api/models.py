"""Module containing the models used for the API.

The classes here can be used independently of the API.

When instantiating an :class:`Episode`, :class:`Show`, :class:`Season`, or :class:`User`
the ``api`` parameter is optional.
If it is specified, that object will be used to make calls to the
API when needed.

For example, :meth:`Episode.season <Episode.season>` would make a call to the API.
If ``api`` is not specified, ``NotImplementedError`` will be raised if a method that
needs the api is called.

"""

import os
from functools import wraps

import m3u8


def api_method(func):
    """Decorator for that methods needing access to the api.

    This decorator ensures that methods that need to make a call to the
    api are only run if access tot he api is available.
    If access to it is not available, ``NotImplementedError`` will be raised.

    """
    @wraps(func)
    def api_call(*args, **kwargs):
        if args[0]._api:
            return func(*args, **kwargs)
        else:
            raise NotImplementedError
    return api_call


class ApiObject(object):
    """Base class for resources available from the API.

    Resources such as Episodes, Seasons, Shows, and Users should inherit from this class.

    """

    def __init__(self):  # noqa: D102
        self._thumbnail = {}

    def _build(self, model_json):
        """Assemble an object from a JSON representation.

        Uses ``self.attrs`` to pull values from ``model_json`` and create object attributes.

        Args:
            model_json: JSON representation of an API resource.

        Raises:
            KeyError: if the key from ``self.attrs`` is not a key in ``model_json``

        """
        for key, value in self.attrs.items():
            try:
                # TODO use setattr(self, key, value) instead?
                self.__dict__.update({key: ApiObject._get_from_dict(model_json, value)})
            except KeyError:
                self.__dict__.update({key: None})

    @staticmethod
    def _get_from_dict(data_dict, map_list):
        """Retrieve the value corresponding to ``map_list`` in ``data_dict``.

        If ``map_list`` is a string, it is used directly as a key of ``data_dict``.
        If ``map_list`` is a list or tuple, each item in it is used recusively as a key.

        Args:
            data_dict (dict): The dictionary to retrieve value from.
            map_list (list, tuple or str): The key(s) to use in data_dict.

        Returns:
            The value corresponding to the given key(s).

        """
        if isinstance(map_list, (list, tuple)):
            for k in map_list:
                data_dict = data_dict[k]
        else:
            data_dict = data_dict[map_list]
        return data_dict

    @property
    def thumbnail(self):
        """Return the default sized thumbnail URL.

        Default is defined as the smallest.

        """
        for thumb in ["tb", "sm", "md", "lg"]:
            try:
                return self._thumbnail[thumb]
            except KeyError:
                continue
        return None

    def __eq__(self, other):
        """Define equality of two API objects as having the same type and attributes."""
        return (type(self) == type(other) and
                dict((k, self.__dict__[k]) for k in self.attrs.keys()) ==
                dict((k, other.__dict__[k]) for k in other.attrs.keys()))

    def __repr__(self):
        """Nicer printing of API objects."""
        return str(dict((k, self.__dict__[k]) for k in self.attrs.keys()))


class Show(ApiObject):
    """Class representing a Show.

    Attributes:
        id_ (int):           Identifier of the show.
        name (str):          The name of the show.
        summary (str):       Summary of the show.
        thumbnail (str):     URL of the default sized thumbnail of the Show.
        cover_picture (str): URL of the default sized cover_picture of the Show.
        season_count (int):  Number of seasons this show has.
        seasons (list):      All of the :class:`Seasons <Season>` of the show.
        episodes (list):     All of the :class:`Episodes <Episode>` of the show.
            This is equivalent to iterating over the show's seasons, and then
            iterating over each season's episodes.
        canonical_url (str): URL of the show on the website.
            e.g. http://roosterteeth.com/show/on-the-spot

    """

    def __init__(self, show_json, api=None):
        """Take in a JSON representation of a show and convert it into a Show Object.

        Args:
            show_json (json):       JSON representation of a show resource.
            api (object, optional): Object that implements the API
                (see :class:`~rt_api.api.rt_api`).
                This will be used to make calls to the API when needed.

        """
        super(Show, self).__init__()
        self._api = api
        self.attrs = {
            "id_": "id",
            "name": "name",
            "canonical_url": "canonicalUrl",
            "season_count": "seasonCount",
            "summary": ("summary", "clean")
        }
        self._build(show_json)
        try:
            thumbnails_json = show_json['profilePicture']
            self._thumbnail = Thumbnail(thumbnails_json)
        except KeyError:
            # Show doesnt have thumbnail
            pass
        try:
            cover_picture_json = show_json['coverPicture']
            self._cover_picture = Thumbnail(cover_picture_json)
        except KeyError:
            # Show doesnt have cover picture
            self._cover_picture = {}
        self._seasons = None
        self._episodes = None

    @property
    @api_method
    def seasons(self):
        """Return all seasons of the Show."""
        if not self._seasons:
            self._seasons = self._api.show_seasons(self.id_)
        return self._seasons

    @property
    def episodes(self):
        """Return all the episodes of the Show."""
        if not self._episodes:
            self._episodes = []
            for season in self.seasons:
                self._episodes.extend(season.episodes)
        return self._episodes

    def get_thumbnail(self, quality):
        """Return the URL of the show's thumbnail at specified quality.

        Args:
            quality (str):  possible values are (in order from smallest to largest): "tb", "sm", "md", "lg".

        Returns:
            str: URL of the thumbnail or ``None`` if thumbnail not available at specified quality.

        """
        try:
            return self._thumbnail[quality]
        except KeyError:
            return None

    @property
    def cover_picture(self):
        """Return the default sized cover picture URL.

        If not available, return the next most 'appropriate' sized thumbnail.
        'Most appropriate' is defined as largest, as the cover picture is usually
        used as a large backdrop.

        Returns:
            str: URL of the cover picture or ``None`` if no cover picture is available.

        Examples:
            >>> some_show.cover_picture
            'http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/14a811b0-b0f1-4b08-a65b-1c565d6d153f/original/21-1458935312881-ots_hero.png'

        """
        for picture in ["lg", "tb", "sm", "md"]:
            try:
                return self._cover_picture[picture]
            except KeyError:
                continue
        return None


class Season(ApiObject):
    """Class representing a Season.

    Attributes:
        id_ (int):            Identifier of this season.
        number (int):         The Season number.
        title (str):          Title of the season.
        description (str):    Description of the season.
        episodes (list):      All of the :class:`Episodes <Episode>` of this season.
        show_name (str):      Name of the :class:`Show` this season belongs to.
        show_id (int):        Identifier of the :class:`Show` this season belongs to.
        show (:class:`Show`): The :class:`Show` this season belongs to.

    """

    def __init__(self, season_json, api=None):
        """Take in a JSON representation of a season and convert it into a Season Object.

        Args:
            season_json (json):     JSON representation of a season resource.
            api (object, optional): Object that implements the API
                (see :class:`~rt_api.api.rt_api`).
                This will be used to make calls to the API when needed.

        """
        self._api = api
        self.attrs = {
            "id_": "id",
            "show_name": ("show", "name"),
            "show_id": ("show", "id"),
            "number": "number",
            "title": "title",
            "description": "description"
        }
        self._build(season_json)
        self._show = None
        self._episodes = None

    @property
    @api_method
    def episodes(self):
        """Return all episodes of the Season."""
        if not self._episodes:
            self._episodes = self._api.season_episodes(self.id_)
        return self._episodes

    @property
    @api_method
    def show(self):
        """Return the show this season belongs to."""
        if not self._show:
            self._show = self._api.show(self.show_id)
        return self._show


class Episode(ApiObject):
    """Class representing an Episode.

    Attributes:
        id_ (int):               Identifier of the episode.
        title (str):             Title of the episode.
        number (int):            The number of this episode.
        caption (str):           Caption of the episode.
        description (str):       Description of the episode.
        is_sponsor_only (bool):  Indicates whether or not the episode is only available to sponsor members.
        video (:class:`Video`):  The :class:`Video` object associated with the episode or
                                 ``None`` if no video is available. If the video is sponsor only
                                 and a sponsor user is not currently authenticated then ``video``
                                 will be ``None``.
        length (int):            Length of the episode in seconds.
        thumbnail (str):         URL of the default sized thumbnail of the episode.
        is_watched (bool):       Indicates whether the current user has watched this episode.
            Will default to ``False`` if not currently authenticated as a user.
            Note: It seems that the API doesn't actually set this value.
            Even if you mark an episode as watched, the API returns it as still being unwatched.
        links (list):             List of :class:`Link` objects associated with the episode.
        audio (:class:`Audio`):   The :class:`Audio` object associated with the episode or ``None``.
        canonical_url (str):     URL to the episode on the website.
            e.g. 'http://roosterteeth.com/episode/the-know-game-news-season-1-crytek-shuts-down-studios'.
        site (str):               The 'site' this episode belongs to.
            e.g. 'theKnow'.
        show_name (str):         The name of the :class:`Show` this episode belongs to.
        show_id (int):            Identifier of the :class:`Show` this episode belongs to.
        show (:class:`Show`):     The :class:`Show` object this episode belongs to.
        season_id (int):          Identifier of the :class:`Season` this episode belongs to.
        season (:class:`Season`): The :class:`Season` object this episode belongs to.

    """

    def __init__(self, episode_json, api=None):
        """Take in a JSON representation of an episode and convert it into an Episode Object.

        Args:
            episode_json (json):    JSON representation of an episode resource.
            api (object, optional): Object that implements the API
                (see :class:`~rt_api.api.rt_api`).
                This will be used to make calls to the API when needed.

        """
        super(Episode, self).__init__()
        self._api = api
        self.attrs = {
            "id_": "id",
            "is_sponsor_only": "sponsorOnly",
            "length": "length",
            "title": "title",
            "show_name": ("show", "name"),
            "number": "number",
            "caption": "caption",
            "description": ("description", "clean"),
            "is_watched": "watched",
            "canonical_url": "canonicalUrl",
            "site": "site",  # TODO site should be an enum?
            "show_id": ("show", "id"),
            "season_id": ("season", "id")
        }
        self._build(episode_json)
        self.is_watched = True if self.is_watched == "watched" else False
        try:
            media_json = episode_json['media']
            self.mediagroup = MediaGroup(media_json)
        except KeyError:
            # Episode doesn't have media
            self.mediagroup = None
        try:
            thumbnails_json = episode_json['profilePicture']
            self._thumbnail = Thumbnail(thumbnails_json)
        except KeyError:
            # Episode doesnt have thumbnail
            pass
        self._season = None
        self._show = None

    @property
    @api_method
    def season(self):
        """Return the Season that this episode belongs to."""
        if not self._season:
            self._season = self._api.season(self.season_id)
        return self._season

    @api_method
    def mark_as_watched(self):
        """Mark this episode as watched by current user.

        Note:
            It seems that the API doesn't actually set this value.
            Even if an episode is marked as watched, the API returns it as still being unwatched.

        Raises:
            :class:`~rt_api.api.NotAuthenticatedError`: if not currently authenticated as a user.

        """
        self._api.mark_episode_watched(self.id_)
        self.is_watched = True

    @api_method
    def add_to_queue(self):
        """Add this episode to current user's queue.

        Raises:
            :class:`~rt_api.api.NotAuthenticatedError`: if not currently authenticated as a user.

        """
        self._api.add_episode_to_queue(self.id_)

    @api_method
    def remove_from_queue(self):
        """Remove this episode from current user's queue.

        Raises:
            :class:`~rt_api.api.NotAuthenticatedError`: if not currently authenticated as a user.

        """
        self._api.remove_episode_from_queue(self.id_)

    @property
    def show(self):
        """Return the show this episode belongs to."""
        return self.season.show

    def get_thumbnail(self, quality):
        """Return the url of the episode's thumbnail at specified quality.

        Args:
            quality (str):  possible values are (in order from smallest to largest): "tb", "sm", "md", "lg".

        Returns:
            str: URL of the thumbnail or ``None`` if thumbnail not available at specified quality.

        """
        try:
            return self._thumbnail[quality]
        except KeyError:
            return None

    @property
    def video(self):
        """Return the video object associated with this episode.

        Returns:
            Video: The Video object associated with this episode or ``None``.

        """
        # TODO use a better heuristic for choosing video to return
        try:
            return self.mediagroup.videos[0]
        except (IndexError, AttributeError):
            # Video doesn't exist
            return None

    @property
    def links(self):
        """Return the links associated with this episode."""
        return self.mediagroup.links

    @property
    def audio(self):
        """Return the audio associated with this episode or ``None``."""
        # TODO use a better heuristic for choosing audio to return
        try:
            return self.mediagroup.audio[0]
        except (IndexError, AttributeError):
            # Audio doesn't exist
            return None


class User(ApiObject):
    """Represents a User.

    Attributes:
        id_ (int):             Identifier of the user.
        username (str):        Username of the user.
        name (str):            Name of the user.
        is_sponsor (bool):     ``True`` if user is a sponsor, else ``False``.
        location (str):        Location of the user.
        occupation (str):      Occupation of the user.
        about (str):           About the user.
        sex (str):             Sex of the user.
        display_title (str):   Display title of the user.
        has_used_trial (bool): ``True`` if user has previously used free trial.
        canonical_url (str):   URL of the user on the website.
        queue (list):          List of :class:`Episodes <Episode>` the user has added to their queue.
        thumbnail (str):       URL of the default sized thumbnail of the user.

    """

    # TODO create a setter for user.queue that adds episode to queue ?
    # Should maintain independent list of episodes that were added and then add them to remote end when update()
    # is called. Then clear this list.
    def __init__(self, user_json, api=None):
        """Take in a JSON representation of a user and convert it into a User Object.

        Args:
            user_json (json):       JSON representation of a user resource.
            api (object, optional): Object that implements the API
                (see :class:`~rt_api.api.rt_api`).
                This will be used to make calls to the API when needed.

        """
        super(User, self).__init__()
        self._api = api
        self.attrs = {
            "id_": "id",
            "username": "username",
            "name": "name",
            "is_sponsor": "sponsor",
            "location": "location",
            "occupation": "occupation",
            "about": ("about", "clean"),
            "sex": "sex",
            "display_title": "displayTitle",
            "has_used_trial": "hasUsedTrial",
            "canonical_url": "canonicalUrl"
        }
        self._build(user_json)
        try:
            thumbnails_json = user_json['profilePicture']
            self._thumbnail = Thumbnail(thumbnails_json)
        except KeyError:
            # Episode doesnt have thumbnail
            pass
        self._queue = None
        self.queue_dirty = False

    @property
    @api_method
    def queue(self):
        """Return the user's episode queue.

        Returns:
            (list): List of Episode instances.

        """
        if not self._queue or self.queue_dirty:
            self._queue = list(self._api.user_queue(self.id_))
            self.queue_dirty = False
        return self._queue

    @api_method
    def update(self):
        """Update user details on remote end.

        Should be called after a user's attributes are changed if the changes
        should persist.

        Raises:
            :class:`~rt_api.api.NotAuthenticatedError`: if not currently authenticated as a user,
                or this is attempted on a user that we are not authenticated as.

        Example:
            >>> my_user.name = "NewName"
            >>> my_user.update()

        """
        params = {
            "displayTitle": "display_title",
            "name": "name",
            "sex": "sex",
            "location": "location",
            "occupation": "occupation",
            "about": "about",
        }
        for key, value in params.items():
            params[key] = getattr(self, value)
        self._api.update_user_details(self.id_, **params)

    def get_thumbnail(self, quality):
        """Return the url of user thumbnail at specified quality.

        Args:
            quality (str):  possible values are (in order from smallest to largest): "tb", "sm", "md", "lg".

        Returns:
            str: URL of the thumbnail or ``None`` if thumbnail not available at specified quality.

        """
        try:
            return self._thumbnail[quality]
        except KeyError:
            return None


class Video(object):
    """Encapsulates a video resource.

    A Video represents a HLS video resource.
    It is usually available in multiple qualities.

    Todo:
        Add support for live videos.

    """

    __default_quality = "720P"

    def __init__(self, url, type_):
        """Create a video resource.

        Args:
            url (str):   URL to the index m3u8 file of the video.
            type_ (str): The type of video (e.g. "cdn" or "ustream").

        Example:
            Video("http://example.com/someVideo/index.m3u8", "cdn")

        """
        self.url = url
        self.type = type_
        self.base_url = os.path.dirname(url) + "/"
        self._available_qualities = None
        self.selected_quality = None

    @property
    def available_qualities(self):
        """Return a list of the qualities the video is available in.

        Returns:
            list: A list of the qualities (as resolutions) the video is available in.

        Example:
            >>> some_video.available_qualities
            ["720P", "480P"]

        """
        if not self._available_qualities:
            self._load_available_qualities()
        # Return a copy of quality list
        return list(self._available_qualities)

    def _load_available_qualities(self):
        """Populate ``self._available_qualities`` with the available quantities.

        A network call will be made to load the associated m3u8 playlist.

        """
        self._available_qualities = {}
        m3u8_obj = m3u8.load(self.url)
        for playlist in m3u8_obj.playlists:
            self._available_qualities["%dP" % playlist.stream_info.resolution[1]] = playlist.uri

    # TODO convert get_quality and set_selected_quality() to a property?
    def get_quality(self, quality=None):
        """Return the chosen quality if specified.

        If quality is specified, that will be returned, otherwise:
        If a quality has previously been selected return that, otherwise:
        Return default quality (720P).

        Args:
            quality(str): Resolution of video. Should be in format <resolution>P

        Returns:
            str: The full URL of the video at the specified quality.

        Example:
            >>> some_video.get_quality()
            'http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/c762632a-b8de-4859-962d-607d8e77ccc4/NewHLS-720P.m3u8'

            >>> some_video.get_quality(quality="360P")
            'http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/c762632a-b8de-4859-962d-607d8e77ccc4/NewHLS-360P.m3u8'

        """
        if quality:
            # Return the specified quality
            return self._get_quality(quality)
        else:
            if self.selected_quality:
                # Return the previously selected quality
                return self.base_url + self.selected_quality
            else:
                # A quality hasn't been selected so return default quality
                return self._get_quality(Video.__default_quality)

    def _get_quality(self, quality):
        """Retrieve the video at the specified quality.

        Args:
            quality (str): Resolution of video. Should be in format <resolution>P

        Returns:
            str: The full URL of the video at the specified quality.

        """
        if not self._available_qualities:
            self._load_available_qualities()
        try:
            return self.base_url + self._available_qualities[quality]
        except KeyError:
            # Chosen quality not available
            # TODO fallback to Video.__default_quality with a warning?
            pass

    def set_selected_quality(self, quality):
        """Set the preferred quality of this video.

        Subsequent calls to :meth:`~rt_api.models.Video.get_quality`
        will return this selected quality (if no quality argument is given to it).

        Args:
            quality(str): Resolution of video. Should be in format <resolution>P

        Raises:
            KeyError: if the specified quality is not available.

        Example:
            >>> set_selected_quality("480P")
            >>> get_quality()
            'http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/c762632a-b8de-4859-962d-607d8e77ccc4/NewHLS-480P.m3u8'

        """
        if not self._available_qualities:
            self._load_available_qualities()
        self.selected_quality = self._available_qualities[quality]


class Audio(object):
    """Encapsulates an audio resource.

    Attributes:
        url (str):       URL of the audio resource.
        container (str): The container format of the audio resource.

    """

    def __init__(self, url, container):
        """Create an audio resource.

        Args:
            url (str):       URL of the audio resource.
            container (str): The container format of the audio resource  e.g "mp3".

        """
        self.url = url
        self.container = container


class Link(object):
    """Encapsulates a link resource.

    Attributes:
        url (str):   URL of the link resource.
        title (str): The title of the Link resource.
        thumbnail (:obj:`Thumbnail`): The Thumbnail object that represents this Link.

    """

    def __init__(self, url, title, thumbnail=None):
        """Create a Link resource.

        Args:
            url (str):   URL of the Link resource.
            title (str): The title of the Link resource.
            thumbnail (:obj:`Thumbnail`, optional): The Thumbnail object that represents this Link.
                (Default value = ``None``).

        """
        self.url = url
        self.title = title
        self.thumbnail = thumbnail


class Thumbnail(dict):
    """Represents the available thumbnails of an API resource.

    The keys of the dictionary are the qualities the thumbnail is
    available in: "tb", "sm", "md", "lg".
    The corresponding values are the URL of the thumbnail at that quality.

    """

    def __init__(self, thumbnail_json):
        """Create a Thumbnail resource.

        Args:
            thumbnail_json (json): JSON representation of a thumbnail.

        """
        super(Thumbnail, self).__init__()
        if thumbnail_json['type'] == "picture":
            items = thumbnail_json['content']
            for key in items.keys():
                self[key] = items[key]


class MediaGroup(object):
    """Class that encapsulates all the media items of an Episode.

    An episode may have multiple videos, audio items, and links associated with it.

    Attributes:
        videos (list): A list of all the :class:`.Video` items of an episode.
        audio (list):  A list of all the :class:`.Audio` items of an episode.
        links (list):  A list of all the :class:`.Link` items of an episode.

    """

    def __init__(self, media_json):
        """Create a MediaGroup resource.

        Args:
            media_json (json): JSON representation of the media resource.

        """
        self.videos = []
        self.audio = []
        self.links = []
        if "videos" in media_json:
            for item in media_json["videos"]:
                url = item["content"]["url"]  # Extract url from json
                type_ = item["content"]["type"]  # Extract type from json
                video_item = Video(url, type_)
                # Add video item to mediagroup
                self.videos.append(video_item)
        if "audioFiles" in media_json:
            for item in media_json["audioFiles"]:
                for key, value in item["content"].items():
                    container = key
                    url = value
                    audio_item = Audio(url, container)
                    self.audio.append(audio_item)  # Add audio item to mediagroup
        if "links" in media_json:
            for item in media_json["links"]:
                title = item["content"]["title"]
                url = item["content"]["link"]
                thumbnails_json = item["content"]["picture"]
                thumbnail = Thumbnail(thumbnails_json)
                link_item = Link(url, title, thumbnail=thumbnail)
                self.links.append(link_item)  # Add link item to mediagroup
