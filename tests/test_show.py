import requests
from httmock import HTTMock

import pytest
from rt_api import models

from .context import mock_shows


@pytest.mark.mocktest
class TestShow(object):

    def test_regular_show(self):
        with HTTMock(mock_shows.regular_show_response):
            show_data = requests.get("https://roosterteeth.com/api/v1/shows/55")
            show = models.Show(show_data.json())
            # Test attributes
            assert show.id_ == 55
            assert show.season_count == 7
            assert show.summary == "Rooster Teeth's official game show!  A live half hour of fast-paced laughs as host Jon Risinger puts two RT teams on the spot for points and mayhem."
            assert show.canonical_url == "http://roosterteeth.com/show/on-the-spot"
            assert show.name == "On The Spot"
            assert show.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/51f48d21-5c15-4211-b3e8-837386bf1b1a/tb/2037887-1467141869039-On_the_Spot_Podcast_Thumbnail.jpg"
            assert show.get_thumbnail("sm") == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/51f48d21-5c15-4211-b3e8-837386bf1b1a/sm/2037887-1467141869039-On_the_Spot_Podcast_Thumbnail.jpg"
            assert show.cover_picture == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/14a811b0-b0f1-4b08-a65b-1c565d6d153f/original/21-1458935312881-ots_hero.png"

    def test_missing_name_show(self):
        with HTTMock(mock_shows.missing_name_show_response):
            show_data = requests.get("https://roosterteeth.com/api/v1/shows/55")
            show = models.Show(show_data.json())
            assert show.name is None

    def test_missing_cover_picture(self):
        with HTTMock(mock_shows.missing_cover_picture_show_response):
            show_data = requests.get("https://roosterteeth.com/api/v1/shows/55")
            show = models.Show(show_data.json())
            assert show.cover_picture is None

    def test_missing_thumbnail_picture(self):
        with HTTMock(mock_shows.missing_all_thumbnail_show_response):
            show_data = requests.get("https://roosterteeth.com/api/v1/shows/55")
            show = models.Show(show_data.json())
            assert show.get_thumbnail("lg") is None
