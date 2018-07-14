import json
import os

import pytest
import vcr

from rt_api import models

from .context import auth

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/season")


@pytest.mark.usefixtures("auth")
class TestSeason(object):

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/seasons/test_regular_season.yaml')
    def test_regular_season(self):
        season_data = self.auth.get("https://roosterteeth.com/api/v1/seasons/455")
        season = models.Season(season_data.json())
        # Test attributes
        assert season.id_ == 455
        assert season.show_name == "On The Spot"
        assert season.show_id == 55
        assert season.number == 7
        assert season.title == "Season 7"
        assert season.description == ""
        assert season.thumbnail is None

    def test_missing_title_season(self):
        with open(os.path.join(TEST_PREFIX, "missing_title_season.json"), "r") as resp:
            season_data = json.loads(resp.read())
            season = models.Season(season_data)
            # Test attributes
            assert season.title is None
