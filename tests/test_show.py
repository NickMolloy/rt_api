import json
import os

import pytest
import vcr

from rt_api import models

from .context import auth

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/show")


@pytest.mark.usefixtures("auth")
class TestShow(object):

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/shows/test_regular_show.yaml')
    def test_regular_show(self):
        show_data = self.auth.get("https://roosterteeth.com/api/v1/shows/55")
        show = models.Show(show_data.json())
        # Test attributes
        assert show.id_ == 55
        assert show.season_count == 12
        assert show.summary == "Rooster Teeth's official game show!  A live half hour of fast-paced laughs as host Jon Risinger puts two RT teams on the spot for points and mayhem."
        assert show.canonical_url == "https://roosterteeth.com/show/on-the-spot"
        assert show.name == "On The Spot"
        assert show.thumbnail == "https://s3.amazonaws.com/rtv3.image.cdn.roosterteeth.com/store/e8d10356-958f-47c7-b66b-924d5bab5554.jpg/tb/OnTheSpotSquare.jpg"
        for quality in models.Thumbnail.qualities:
            assert show.get_thumbnail(quality) == "https://s3.amazonaws.com/rtv3.image.cdn.roosterteeth.com/store/e8d10356-958f-47c7-b66b-924d5bab5554.jpg/{}/OnTheSpotSquare.jpg".format(quality)
        assert show.cover_picture == "https://s3.amazonaws.com/rtv3.image.cdn.roosterteeth.com/store/64f97401-2a32-4bbb-a9e6-5f9035fa680c.jpg/original/OnTheSpotHero2.jpg"

    def test_missing_name_show(self):
        with open(os.path.join(TEST_PREFIX, "missing_name_show.json"), "r") as resp:
            show_data = json.loads(resp.read())
            show = models.Show(show_data)
            assert show.name is None

    def test_missing_cover_picture(self):
        with open(os.path.join(TEST_PREFIX, "missing_cover_picture_show.json"), "r") as resp:
            show_data = json.loads(resp.read())
            show = models.Show(show_data)
            assert show.cover_picture is None

    def test_missing_thumbnail_picture(self):
        with open(os.path.join(TEST_PREFIX, "missing_all_thumbnail_show.json"), "r") as resp:
            show_data = json.loads(resp.read())
            show = models.Show(show_data)
            assert show.thumbnail is None
            assert show.get_thumbnail("lg") is None
