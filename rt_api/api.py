"""Module containing the interface to the Api.

Currently access to Episodes, Shows, Seasons, and Users is provided.

Todo:
    * Get live videos
    * Login/Authenticate with Facebook
    * Feed for News
    * Feed for Forum topics
    * Registration/Sign up
    * Signing up for Sponsorship
    * Password update and reset
    * Changing user profile picture
    * Caching responses

"""

import posixpath
from functools import wraps

import requests
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import (AccessDeniedError,
                                            InvalidClientError,
                                            MissingTokenError)
from requests_oauthlib import OAuth2Session

from rt_api import models

END_POINT = "https://roosterteeth.com/api/v1/"
AUTH_URL = "https://roosterteeth.com/authorization/oauth-access-token"
CLIENT_ID = "aToGIjvJ8Lofqmso"
CLIENT_SECRET = "oW3CtlpnXRznUUiWLXzmaIQryFBfGmNt"


def authenticated(func):
    """Decorator for methods that make api calls that need authentication.

    This decorator will ensure that methods that need authentication will
    only be called if the api instance is authenticated.
    Otherwise a ``NotAuthenticatedError`` will be raised.

    """
    @wraps(func)
    def auth_call(*args, **kwargs):
        api = args[0]
        if not api.user_id and not api._me:
            raise NotAuthenticatedError
        else:
            return func(*args, **kwargs)
    return auth_call


class Api(object):
    """Main class of the API.

    Create an instance of this to access the api.

    """

    def __init__(self, api_key=None):
        """Create an api object.

        Args:
            api_key (str, optional): api key to use.
                If one is not supplied, a default one will be generated and used.

        """
        self.__session = requests.Session()
        self.user_id = None
        self._me = None
        if api_key:
            self.__token = api_key
        else:
            self._get_token()
        self.__session.headers.update({"Authorization": self.__token})

    @property
    def token(self):
        """Return the token currently in use by the api.

        Returns:
            str: Token currently in use by this instance.

        """
        return self.__token

    def _get_token(self):
        """Get an API token.

        Raises:
            AuthenticationError: if getting token fails.

        """
        client = BackendApplicationClient(client_id=CLIENT_ID)
        oauth = OAuth2Session(client=client)
        # Retry auth if error (to get around intermittent failures)
        latest_exception = None
        for i in range(3):
            try:
                token = oauth.fetch_token(
                    token_url=AUTH_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
                self.__token = token["access_token"]
                self.__session = oauth
                self._me = None
                return
            except (AccessDeniedError, InvalidClientError, MissingTokenError) as e:
                latest_exception = e
                continue
        raise AuthenticationError("Failed to get authentication token: {0}".format(latest_exception))

    def authenticate(self, username, password):
        """Authenticate to the API using a username and password.

        The token retrieved will be used for future API requests, and will
        persist only until the api object is destroyed. If you wish to use
        this token in future sessions, you should save the token and use it
        again when creating an api object.

        The token retrieved is linked to the credentials used to authenticate.
        Using the token in the api mean actions performed will be done as the
        user with those credentials.

        Args:
            username (str): Username of Rooster Teeth account.
            password (str): Password of Rooster Teeth account.

        Returns:
            str: Token retrieved from API on successful authentication.

        Raises:
            AuthenticationError: if authentication fails.

        """
        # TODO retry auth if error (to get around intermittent failures)
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "password",
            "scope": "user.access",
            "username": username,
            "password": password
        }
        result = self.__session.post(AUTH_URL, data=payload)
        try:
            data = result.json()
        except:
            raise AuthenticationError("Failed to get authentication token: {0}  {1}".format(
                result.status_code, result.text))
        if result.status_code == 401:
            error = data["error_description"]
            raise AuthenticationError(error)
        elif result.status_code == 201:
            # Success
            self.__session = requests.Session()
            self.__token = data['access_token']
            self.__session.headers.update({"Authorization": self.__token})
            self.user_id = int(result.headers.get("X-User-Id"))
            return self.__token

    @property
    def me(self):
        """Access the :class:`~rt_api.models.User` object for the authenticated user.

        If not authenticated as a user, returns None.

        Returns:
            User: The user object corresponding to authenticated user or None.

        """
        if not self._me and self.user_id:
            self._me = self.user(self.user_id)
        elif not self._me and not self.user_id:
            # No user id, and no user, so cant find authenticated user
            return None
        return self._me

    def __get_data(self, url, params=None):
        """Get the data at the given URL, using supplied parameters.

        Args:
            url (str):               The URL to retrieve data from.
            params (dict, optional): Key-value pairs to include when making the request.

        Returns:
            json: The JSON response.

        """
        response = self.__session.get(url, params=params)
        # Check status code
        if response.status_code == 401:
            # TODO Bad api key
            response.raise_for_status()
        elif response.status_code == 404:
            # Api Item does not exist
            return None
        elif response.status_code != requests.codes.ok:
            response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            # Parsing json response failed
            pass

    def __build_response(self, path, model_class):
        """Retrieve data from given path and load it into an object of given model class.

        Args:
            path (str):         Path of API to send request to.
            model_class (type): The type of pbject to build using the response from the API.

        Returns:
            object: Instance of the specified model class.

        """
        data = self.__get_data(posixpath.join(END_POINT, path))
        if not data:
            # TODO raise exception complaining that no data was retrieved from api?
            return None
        return model_class(data, self)

    def __get_multiple(self, model_class, path, key=None, **kwargs):
        """Retrieve from API endpoint that returns a list of items.

        Args:
            model (type): The type of object to build using the response from the API.
            path (str):   The path of API to send request to.
            key (str, optional): Key to use as index into each item of data from API.
            **kwargs:     Key-value pairs to include when making the request.

        Returns:
            list: A list containing items of type model_class.

        """
        url = posixpath.join(END_POINT, path)
        data = self.__get_data(url, kwargs)
        if not data:
            return None
        items = []
        for json_item in data:
            item = json_item[key] if key else json_item
            items.append(model_class(item, self))
        return items

    def __pager(self, model_class, path, count=20, page=1, **kwargs):
        """Paginate an API resource.

        This is a generator that yields a single result.
        It handles retrieving new pages from the Api as needed.

        Args:
            model_class (type): The type of model that will be instantiate for api results.
            path (str):         Path of API to send request to.
            count (int):        Number of Api items per page (Default value = 20).
            page (int):         The page to start the generator from (Default value = 1).
            **kwargs:           Key-value pairs to include when making the request.

        Yields:
            object: An instance of ``model_class``.

        """
        while True:
            items = self.__get_multiple(model_class, path, page=page, count=count, **kwargs)
            if items:
                for item in items:
                    yield item
                page += 1
            else:
                break

    def episode(self, episode_id):
        """Retrieve the episode corresponding to the specified id.

        Args:
            episode_id (int): ID of the episode to retrieve.

        Returns:
            Episode: Episode instance.

        """
        return self.__build_response("episodes/{0}".format(episode_id), models.Episode)

    def episodes(self, site=None, page=1, count=20):
        # TODO add more explanation about how iterable works (see shows() doc)
        """Get latest episodes from feed.

        Args:
            site (str, optional): If specified, only episodes from this site will be returned.
            page (int):           The page to start from (Default value = 1).
            count (int):          Number of Episodes per page (Default value = 20).

        Returns:
            iterable: An iterable collection of :class:`Episodes <rt_api.models.Episode>`
            from 'latest' feed.

        """
        return self.__pager(models.Episode, "feed/", key="item", type="Episode", count=count, page=page, site=site)

    def season(self, season_id):
        """Retrieve the season corresponding to the specified id.

        Args:
            season_id (int): ID of the season to retrieve.

        Returns:
            Season: Season instance.

        """
        return self.__build_response("seasons/{0}".format(season_id), models.Season)

    def season_episodes(self, season_id):
        """Retrieve the episodes that belong to the season with the specified id.

        Args:
            season_id (int): ID of the season.

        Returns:
            list: A list of :class:`~rt_api.models.Episode` objects.

        """
        return self.__get_multiple(models.Episode, "seasons/{0}/episodes".format(season_id))

    def show_seasons(self, show_id):
        """Get the seasons belonging to show with specified ID.

        Args:
            show_id (int): ID of the show.

        Returns:
            list: A list of :class:`~rt_api.models.Season` objects.

        """
        return self.__get_multiple(models.Season, "shows/{0}/seasons/".format(show_id))

    def show(self, show_id):
        """Return show with given id.

        Args:
            show_id (int): ID of the show to retrieve.

        Returns:
            Show: Show instance.

        """
        return self.__build_response("shows/{0}".format(show_id), models.Show)

    def shows(self, site=None, page=1, count=20):
        """Return an iterable feed of :class:`Shows <rt_api.models.Show>`.

        This will return an iterable, which starts at the specified page,
        and can be iterated over to retrieve all shows onwards.

        Under the hood, as this is iterated over, new pages are fetched from the API.
        Therefore, the size of ``count`` will dictate the delay this causes.

        A larger ``count`` means larger delay, but fewer total number of
        pages will need to be fetched.

        Args:
            site (str):  Only return shows from specified site, or all sites if None.
            page (int):  The page to start from (Default value = 1).
            count (int): Number of Shows per page (Default value = 20).

        Returns:
            iterable: An iterable collection of :class:`Shows <rt_api.models.Show>`.

        Example::

            r = rt_api()
            show_feed = r.shows(site="theKnow")
            for show in show_feed:
                print(show)

        """
        # TODO 'site' should be an Enum?
        return self.__pager(models.Show, "shows/", count=count, page=page, site=site)

    def user(self, user_id):
        """Retrieve the User with the specified id.

        Args:
            user_id (int): ID of the user to retrieve.

        Returns:
            User: User instance.

        """
        return self.__build_response("users/{0}".format(user_id), models.User)

    @authenticated
    def update_user_details(self, user_id, **kwargs):
        """Update the details of the user with the specified id.

        You must be authenticated as the user to be updated.
        Attributes should be specified as keyword arguments.

        Possible keyword arguments:
            displayTitle,
            name,
            sex,
            location,
            occupation,
            about

        Note:
            All attributes will be updated. If an attribute is not specified,
            the remote end assumes it to be empty and sets it as such.

        Args:
            user_id (int): ID of the user to update.

        Raises:
            NotAuthenticatedError: if not currently authenticated as a user,
                or this is attempted on a user not authenticated as.

        """
        if user_id != self.user_id:
            # Attempting to update a user we are not authenticated as.
            # This will result in a 401 response, so don't bother sending request.
            raise NotAuthenticatedError
        path = "users/{0}".format(user_id)
        url = posixpath.join(END_POINT, path)
        data = kwargs
        response = self.__session.put(url, data=data)
        response.raise_for_status()
        # Update 'me' user with new details
        # TODO update existing user object instead of creating new one and replacing reference
        self._me = models.User(response.json(), self)

    def user_queue(self, user_id, page=1, count=20):
        # TODO add more explanation about how iterable works (see shows() doc)
        """Retrieve the episodes in specified user's queue.

        Args:
            user_id (int): The ID of the user to get the queue of.
            page (int):    The page to start from (Default value = 1).
            count (int):   Number of Episodes per page (Default value = 20).

        Returns:
            iterable: Iterable of :class:`~rt_api.models.Episode` instances.

        """
        return self.__pager(models.Episode, "users/{0}/queue".format(user_id), page=page, count=count)

    @authenticated
    def add_episode_to_queue(self, episode_id):
        """Add specified episode to current user's queue.

        Args:
            episode_id (int): ID of the episode to add to user's queue.

        Returns:
            str: Success message from API or None.

        Raises:
            NotAuthenticatedError: if not currently authenticated as a user.

        """
        path = "episodes/{0}/add-to-queue".format(episode_id)
        url = posixpath.join(END_POINT, path)
        response = self.__session.post(url)
        response.raise_for_status()
        # Mark user queue as needing refresh
        self.me.queue_dirty = True
        return response.headers.get("X-Message")

    @authenticated
    def remove_episode_from_queue(self, episode_id):
        """Remove specified episode from current user's queue.

        Args:
            episode_id (int): ID of the episode to remove from user's queue.

        Returns:
            str: Success message from API or None.

        Raises:
            NotAuthenticatedError: if not currently authenticated as a user.

        """
        path = "episodes/{0}/remove-from-queue".format(episode_id)
        url = posixpath.join(END_POINT, path)
        response = self.__session.delete(url)
        response.raise_for_status()
        # Mark user queue as needing refresh
        self.me.queue_dirty = True
        return response.headers.get("X-Message")

    @authenticated
    def mark_episode_watched(self, episode_id):
        """Mark the specified episode as having been watched by the current user.

        Args:
            episode_id (int): ID of the episode to mark as having been watched.

        """
        path = "episodes/{0}/mark-as-watched".format(episode_id)
        url = posixpath.join(END_POINT, path)
        response = self.__session.put(url)
        response.raise_for_status()

    def search(self, query, include=None):
        """Perform a search for the specified query.

        Currently only supports searching for Episodes, Shows, and Users.
        Unfortunately, the Api only returns up to 10 of each resource type.

        Args:
            query (str): The value to search for.
            include (list, optional): A list of types to include in the results (Default value = None).
                If ``include`` is specified, only objects of those types will be returned in the results.

        Example:
            Search for "funny", only in shows and episodes.

            .. code-block::  python

                search("funny", include=[rt_api.models.Show, rt_api.models.Episode])

        Returns:
            list: The search results.

        """
        url = posixpath.join(END_POINT, "search/?q={0}".format(query))
        data = self.__get_data(url)
        mapping = {
            "episodes": models.Episode,
            "shows": models.Show,
            "users": models.User
        }
        items = []
        for result_set in data:
            # Try to find corresponding model for this result type
            model_key = None
            for result_type in mapping:
                if result_type in result_set.keys():
                    model_key = result_type
                    break
            if model_key:
                # Check if we are doing any filtering
                if include and mapping[model_key] not in include:
                    # This model is not in 'include', so skip it
                    continue
                for item in result_set[model_key]:
                    items.append(mapping[model_key](item))
        return items


class AuthenticationError(Exception):
    """Raised when an error is encountered while performing authentication."""

    pass


class NotAuthenticatedError(Exception):
    """Raised if an action requiring authentication is attempted but no account is authenticated."""

    pass
