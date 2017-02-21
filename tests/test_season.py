import requests
from httmock import HTTMock

import pytest
from rt_api import models

from .context import mock_seasons


@pytest.mark.mocktest
class TestSeason(object):

    def test_regular_season(self):
        with HTTMock(mock_seasons.regular_season_response):
            season_data = requests.get("https://roosterteeth.com/api/v1/seasons/455")
            season = models.Season(season_data.json())
            # Test attributes
            assert season.id_ == 455
            assert season.show_name == "On The Spot"
            assert season.show_id == 55
            assert season.number == 7
            assert season.title == "Season 7"
            assert season.description == ""

    def test_missing_title_season(self):
        with HTTMock(mock_seasons.missing_title_season_response):
            season_data = requests.get("https://roosterteeth.com/api/v1/seasons/455")
            season = models.Season(season_data.json())
            # Test attributes
            assert season.title is None
