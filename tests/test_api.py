import os

import itertools

import requests
from httmock import HTTMock, all_requests
from requests.exceptions import HTTPError

import pytest
import rt_api
import vcr
from flaky import flaky
from rt_api import api


class TestApi(object):

    def setup_method(self, test_method):
        self.api = rt_api.api.Api()

    def teardown_method(self, test_method):
        self.api._Api__session.close()

    def test_non_json_response(self):
        with HTTMock(non_json_episode_response):
            episode = self.api.episode(20434)
            assert episode is None

    def test_unauthorized(self):
        with HTTMock(unauthorized_episode_response):
            with pytest.raises(requests.exceptions.HTTPError) as excinfo:
                episode = self.api.episode(20434)
            assert excinfo.value.response.status_code == 401

    def test_other_error_code(self):
        with HTTMock(none_ok_episode_response):
            with pytest.raises(requests.exceptions.HTTPError) as excinfo:
                episode = self.api.episode(20434)
            assert excinfo.value.response.status_code == 500

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_episode.yaml')
    def test_get_episode(self):
        episode = self.api.episode(20434)
        assert episode is not None
        assert episode.number == 35
        assert episode.canonical_url == "http://roosterteeth.com/episode/on-the-spot-season-3-15"
        assert episode.caption == "The only reason Joel let me put out a video like this was because I agreed to let him talk to me about the Fed raising interest rates and how the Chinese economy is affecting the value of gold. I did this for you guys. Please don't let it be in vain."
        assert episode.show_name == "On The Spot"
        assert episode.id_ == 20434
        assert episode.description == "The only reason Joel let me put out a video like this was because I agreed to let him talk to me about the Fed raising interest rates and how the Chinese economy is affecting the value of gold. I did this for you guys. Please don't let it be in vain."
        assert episode.show_id == 55
        assert episode.site == "roosterTeeth"
        assert episode.is_sponsor_only is False
        assert episode.season_id == 231
        assert episode.title == "Shibas Love Joel Heyman - On The Spot: Just the Bits"
        assert episode.length == 288

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_non_existant_episode.yaml')
    def test_get_nonexistant_episode(self):
        episode = self.api.episode(99999999999)
        assert episode is None

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episode_equality.yaml')
    def test_episode_equality(self):
        ep1 = self.api.episode(20434)
        ep2 = self.api.episode(20845)
        assert ep1 != ep2  # Different episodes should not be equal
        ep3 = self.api.episode(20434)
        assert ep1 == ep3  # Same episode, different objects should be equal

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/season_equality.yaml')
    def test_season_equality(self):
        season1 = self.api.season(455)
        season2 = self.api.season(456)
        assert season1 != season2  # Different seasons should not be equal
        season3 = self.api.season(455)
        assert season1 == season3  # Same season, different objects should be equal

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/show_equality.yaml')
    def test_show_equality(self):
        show1 = self.api.show(55)
        show2 = self.api.show(56)
        assert show1 != show2  # Different shows should not be equal
        show3 = self.api.show(55)
        assert show1 == show3  # Same show, different objects should be equal

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/user_equality.yaml')
    def test_user_equality(self):
        user1 = self.api.user(2269568)
        user2 = self.api.user(2269569)
        assert user1 != user2  # Different users should not be equal
        user3 = self.api.user(2269568)
        assert user1 == user3  # Same user, different objects should be equal

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/inequality.yaml')
    def test_inequality(self):
        """Check that objects with same id but different type are not equal"""
        id_ = 50
        ep = self.api.episode(id_)
        season = self.api.season(id_)
        show = self.api.show(id_)
        user = self.api.user(id_)
        items = [ep, season, show, user]
        for item in items:
            assert items.count(item) == 1

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episode_to_season_traversal.yaml')
    def test_episode_to_season_traversal(self):
        episode = self.api.episode(20434)
        season = episode.season
        assert season is not None
        assert self.api.season(231) == season

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episode_to_show_traversal.yaml')
    def test_episode_to_show_traversal(self):
        episode = self.api.episode(20434)
        show = episode.show
        assert show is not None
        assert self.api.show(55) == show

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_season.yaml')
    def test_get_season(self):
        season = self.api.season(231)
        assert season is not None
        assert season.id_ == 231
        assert season.show_name == "On The Spot"
        assert season.show_id == 55
        assert season.number == 3
        assert season.title == "Season 3"
        assert season.description == ""

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_non_existant_season.yaml')
    def test_get_nonexistant_season(self):
        season = self.api.season(99999999999)
        assert season is None

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/season_to_episode_traversal.yaml')
    def test_season_to_episodes_traversal(self):
        season = self.api.season(231)
        episodes = season.episodes
        assert episodes is not None
        assert len(episodes) == 15
        ep = self.api.episode(20375)
        assert episodes[1] == ep

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/season_to_show_traversal.yaml')
    def test_season_to_show_traversal(self):
        season = self.api.season(231)
        show = season.show
        assert show is not None
        assert show == self.api.show(55)

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_show.yaml')
    def test_get_show(self):
        show = self.api.show(55)
        assert show is not None
        assert show.id_ == 55
        assert show.name == "On The Spot"
        assert show.canonical_url == "http://roosterteeth.com/show/on-the-spot"
        assert show.season_count == 8
        assert show.summary == "Rooster Teeth's official game show!  A live half hour of fast-paced laughs as host Jon Risinger puts two RT teams on the spot for points and mayhem."

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_shows_with_count.yaml')
    def test_get_shows_with_count(self):
        shows = self.api.shows(count=5)
        assert shows.gi_frame.f_locals['count'] == 5
        page = 0
        for index, show in enumerate(shows):
            if index == 10:
                break
            if index % 5 == 0:
                page += 1
            assert type(show) == rt_api.models.Show
            assert shows.gi_frame.f_locals['page'] == page

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_shows_with_page.yaml')
    def test_get_shows_with_page(self):
        # Default page size is 20
        pg1_shows = itertools.islice(self.api.shows(page=1), 20)
        pg2_shows = itertools.islice(self.api.shows(page=2), 20)
        for show in pg2_shows:
            assert show not in pg1_shows

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_shows_with_site.yaml')
    def test_get_shows_with_site(self):
        shows = self.api.shows(site="funhaus")
        # API doesn't include site in a Show, so we need to check it's episodes
        for index, show in enumerate(shows):
            episode = show.seasons[0].episodes[0]
            assert episode.site == "funhaus"
            if index == 25:
                # Don't process more than 25 items
                break

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_non_existant_show.yaml')
    def test_get_nonexistant_show(self):
        show = self.api.show(99999999999)
        assert show is None

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/show_to_seasons_traversal.yaml')
    def test_show_to_seasons_traversal(self):
        show = self.api.show(55)
        seasons = show.seasons
        assert seasons is not None
        assert len(seasons) == 8
        season = self.api.season(455)
        assert season == seasons[1]

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/show_to_episodes_traversal.yaml')
    def test_show_to_episodes_traversal(self):
        show = self.api.show(52)
        episodes = show.episodes
        assert episodes is not None
        assert len(episodes) == 21
        ep = self.api.episode(28661)
        assert ep == episodes[0]

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episodes_from_feed_with_count.yaml')
    def test_get_episodes_from_feed_with_count(self):
        episodes = self.api.episodes(count=3)
        assert episodes.gi_frame.f_locals['count'] == 3
        page = 0
        for index, item in enumerate(episodes):
            if index == 10:
                break
            if index % 3 == 0:
                page += 1
            assert type(item) == rt_api.models.Episode
            assert episodes.gi_frame.f_locals['page'] == page

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episodes_from_feed_with_site.yaml')
    def test_get_episodes_from_feed_with_site(self):
        response = self.api.episodes(site="funhaus")
        page = itertools.islice(response, 20)
        for item in page:
            assert type(item) == rt_api.models.Episode
            assert item.site == "funhaus"

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/default_api_key.yaml')
    def test_default_api_key(self):
        """Test that we are able to obtain an API token if a token is not specified."""
        episode = self.api.episode(20434)
        assert episode == self.api.episode(20434)

    @pytest.mark.skipif("rt_user" not in os.environ or "rt_pass" not in os.environ, reason="rt_user or rt_pass not defined in environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/authenticate.yaml')
    def test_authenticate(self):
        """Test that we can authenticate to API with user credentials.

        Test that we are able to retrieve the user object for the now authenticated user.

        Uses credentials in Envirnonment variables:
            rt_user
            rt_pass
            rt_id (optional)

        """
        username = os.environ["rt_user"]
        password = os.environ["rt_pass"]
        token = self.api.authenticate(username, password)
        assert token is not None
        # Check that token was 'stored'
        assert token == self.api.token
        # Check that user_id was set
        assert self.api.user_id is not None
        # Check that token is valid
        episode = self.api.episode(20434)
        if "rt_id" in os.environ:
            assert self.api.user_id == int(os.environ["rt_id"])
        # Check we can get User object for authenticated user
        assert self.api.me is not None

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/bad_authentication.yaml')
    def test_bad_authentication(self):
        """Test that bad username/password is caught."""
        with pytest.raises(api.AuthenticationError) as excinfo:
            token = self.api.authenticate("usernameForUserThatDoesNotExist", "passwordForUserThatDoesNotExist")
        assert str(excinfo.value) == "The user credentials were incorrect."
        assert self.api.user_id is None

    def test_fail_get_token(self):
        """Test that correct exception is raised if getting token fails."""
        with HTTMock(fail_get_token):
            with pytest.raises(api.AuthenticationError):
                self.api._get_token()

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_user.yaml')
    def test_get_user(self):
        """Test that we are able to retrieve a user."""
        user = self.api.user(2269568)
        assert user is not None
        assert user.id_ == 2269568
        assert user.username == "arasabu1"
        assert user.name == "param1"
        assert user.is_sponsor is False
        assert user.location == "param8"
        assert user.occupation == "param4"
        assert user.about == ""
        assert user.sex == "p"
        assert user.display_title == "param2"
        assert user.has_used_trial is True
        assert user.canonical_url == "http://roosterteeth.com/user/arasabu1"
        assert user.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/0ac1b38e-0bdc-4e2e-9971-4fdb478b18d2/tb/embed"
        assert user.get_thumbnail("md") == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/0ac1b38e-0bdc-4e2e-9971-4fdb478b18d2/md/embed"

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_non_existant_user.yaml')
    def test_non_existant_user(self):
        with HTTMock(no_user_response):
            user = self.api.user(0)
            assert user is None

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/get_user_queue.yaml')
    def test_get_user_queue(self):
        user = self.api.user(2269568)
        user_queue = user.queue
        assert user_queue is not None
        ids = [26008, 26013, 20725, 20399, 28767, 3000, 28805, 31430]
        assert len(ids) == len(user_queue)
        for episode in user_queue:
            assert episode.id_ in ids

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/paginated_user_queue.yaml')
    def test_multiple_iteration(self):
        """Test that paginted resources can be iterated over multiple times."""
        user = self.api.user(2269568)
        user_queue = user.queue
        # Iterate once
        count_one = 0
        for page in user_queue:
            count_one += 1
        # Iterate again
        count_two = 0
        for page in user_queue:
            count_two += 1
        assert count_one == count_two

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/authenticated_methods_without_authentication.yaml')
    def test_authenticated_methods_without_authentication(self):
        """Test that methods requiring an authenticated user work properly."""
        # Attempt authenticated action with no user authenticated
        with pytest.raises(api.NotAuthenticatedError):
            self.api.add_episode_to_queue(20434)
        with pytest.raises(api.NotAuthenticatedError):
            self.api.remove_episode_from_queue(20434)
        with pytest.raises(api.NotAuthenticatedError):
            self.api.mark_episode_watched(20434)

    @pytest.mark.skipif("rt_token" not in os.environ, reason="'rt_token' not defined in the environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/use_existing_token.yaml')
    def test_exisiting_api_token(self):
        """Test that an existing api token can be used.

        Requires that 'rt_token' is defined in environment.

        """
        r = api.Api(os.environ["rt_token"])
        assert r.episode(20434) is not None

    @pytest.mark.skipif("rt_user" not in os.environ or "rt_pass" not in os.environ, reason="rt_user or rt_pass not defined in environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/authenticated_methods_with_authentication.yaml')
    def test_authenticated_methods_with_authentication(self):
        self.api.authenticate(os.environ["rt_user"], os.environ["rt_pass"])
        user_queue_before = self.api.me.queue
        user_queue_before_count = len(self.api.me.queue)
        if self.api.episode(20434) not in user_queue_before:
            self.api.add_episode_to_queue(20434)
            assert (user_queue_before_count + 1) == len(self.api.me.queue)
            self.api.remove_episode_from_queue(20434)
            assert user_queue_before_count == len(self.api.me.queue)
        else:
            self.api.remove_episode_from_queue(20434)
            assert (user_queue_before_count - 1) == len(self.api.me.queue)
            self.api.add_episode_to_queue(20434)
            assert user_queue_before_count == len(self.api.me.queue)

    @pytest.mark.skipif("rt_user" not in os.environ or "rt_pass" not in os.environ, reason="rt_user or rt_pass not defined in environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/authenticated_methods_with_authentication.yaml')
    def test_authenticated_methods_with_authentication_on_episode(self):
        """Test add/remove from queue and mark as watched functionality when
        called directly on an episode instance.
        """
        self.api.authenticate(os.environ["rt_user"], os.environ["rt_pass"])
        user_queue_before = self.api.me.queue
        user_queue_before_count = len(self.api.me.queue)
        episode = self.api.episode(20434)
        if episode not in user_queue_before:
            episode.add_to_queue()
            assert (user_queue_before_count + 1) == len(self.api.me.queue)
            episode.remove_from_queue()
            assert user_queue_before_count == len(self.api.me.queue)
        else:
            episode.remove_from_queue()
            assert (user_queue_before_count - 1) == len(self.api.me.queue)
            episode.add_to_queue()
            assert user_queue_before_count == len(self.api.me.queue)

    @pytest.mark.skipif("rt_user" not in os.environ or "rt_pass" not in os.environ, reason="rt_user or rt_pass not defined in environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/mark_as_watched.yaml')
    def test_mark_as_watched(self):
        self.api.authenticate(os.environ["rt_user"], os.environ["rt_pass"])
        episode = self.api.episode(20434)
        episode.mark_as_watched()
        assert episode.is_watched is True
        # This will fail, becuase API doesn't update the watched status.
        # Not sure why this is the case.
        # reloaded_episode = r.episode(20434)
        # assert reloaded_episode.is_watched is True

    def test_get_current_user_when_none(self):
        """Test that None is returned if we attempt to get the current user when we are not authenticated."""
        assert self.api.me is None

    def test_non_json_repsonse_for_authentication(self):
        with HTTMock(non_json_repsonse_for_authentication):
            with pytest.raises(api.AuthenticationError):
                self.api.authenticate("someUsername", "somePassword")

    def test_non_json_repsonse_for_get_token(self):
        with HTTMock(non_json_repsonse_for_authentication):
            with pytest.raises(api.AuthenticationError):
                api.Api()

    @pytest.mark.skipif("rt_user" not in os.environ or "rt_pass" not in os.environ, reason="rt_user or rt_pass not defined in environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/update_user.yaml')
    def test_update_user(self):
        self.api.authenticate(os.environ["rt_user"], os.environ["rt_pass"])
        user = self.api.me
        old_name = self.api.me.name
        new_name = "NewName"
        self.api.update_user_details(self.api.user_id, name=new_name, displayTitle=self.api.me.display_title,
                                     sex=self.api.me.sex, location=self.api.me.location,
                                     occupation=self.api.me.occupation, about=self.api.me.about)
        # Test that 'me' is updated
        assert self.api.me.name == new_name
        # Test that re-retrieved user is updated
        assert self.api.user(self.api.user_id).name == new_name
        self.api.update_user_details(self.api.user_id, name=old_name, displayTitle=self.api.me.display_title,
                                     sex=self.api.me.sex, location=self.api.me.location,
                                     occupation=self.api.me.occupation, about=self.api.me.about)
        assert self.api.me.name == old_name
        assert self.api.user(self.api.user_id).name == old_name

    @pytest.mark.skipif("rt_user" not in os.environ or "rt_pass" not in os.environ, reason="rt_user or rt_pass not defined in environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/update_user_on_user_object.yaml')
    def test_update_user_on_user_object(self):
        self.api.authenticate(os.environ["rt_user"], os.environ["rt_pass"])
        user_id = self.api.user_id
        old_name = self.api.me.name
        new_name = "NewName"
        self.api.me.name = new_name
        self.api.me.update()
        # Test that re-retrieved user is updated
        retrieved_user = self.api.user(user_id)
        assert retrieved_user.name == new_name
        self.api.me.name = old_name
        self.api.me.update()
        retrieved_user = self.api.user(user_id)
        assert retrieved_user.name == old_name

    @pytest.mark.skipif("rt_user" not in os.environ or "rt_pass" not in os.environ, reason="rt_user or rt_pass not defined in environment")
    @vcr.use_cassette('tests/fixtures/vcr_cassettes/credentials/update_other_user.yaml')
    def test_update_other_user(self):
        """Test that exception is raised if we try to update details of a user that is not us."""
        with pytest.raises(api.NotAuthenticatedError):
            self.api.authenticate(os.environ["rt_user"], os.environ["rt_pass"])
            user = self.api.user(30004)
            user.name = "NotUs"
            user.update()

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/search.yml')
    def test_search(self):
        results = self.api.search("funny")
        assert len(results) == 12
        assert self.api.episode(26133) in results
        assert self.api.episode(25964) in results
        assert self.api.show(231) in results
        assert self.api.user(219541) in results
        # Test searching with empty query
        results = self.api.search("")
        assert len(results) == 0

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/search_includes.yml')
    def test_search_includes(self):
        results = self.api.search("stuff", include=[rt_api.models.Episode])
        assert len(results) == 10
        assert self.api.episode(6241) in results
        assert self.api.episode(24637) in results
        results = self.api.search("stuff", include=[rt_api.models.Episode, rt_api.models.User])
        assert len(results) == 16
        assert self.api.episode(6241) in results
        assert self.api.episode(24637) in results
        assert self.api.user(2490245) in results
        assert self.api.user(2756581) in results
        # Test include for model not available in search
        results = self.api.search("stuff", include=[rt_api.models.Season])
        assert len(results) == 0





@all_requests
def non_json_episode_response(url, request):
    return {'status_code': 200, 'content': None}


@all_requests
def unauthorized_episode_response(url, request):
    return {'status_code': 401, 'content': '{"error": "access_denied", "error_message": "The resource owner or authorization server denied the request."}'}


@all_requests
def none_ok_episode_response(url, request):
    return {'status_code': 500, 'content': None}


@all_requests
def fail_get_token(url, request):
    return {'status_code': 401, 'content': '{"error":"invalid_client","error_message":"Client authentication failed."}'}


@all_requests
def non_json_repsonse_for_authentication(url, request):
    return {'status_code': 500, 'content': 'Something went wrong.'}


@all_requests
def no_user_response(url, request):
    return {'status_code': 404}
