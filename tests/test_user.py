import json
import os

import pytest
import vcr

from rt_api import models

from .context import auth

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/user")


@pytest.mark.usefixtures("auth")
class TestUser(object):

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/users/test_regular_user.yaml')
    def test_regular_user(self):
        user_data = self.auth.get("https://roosterteeth.com/api/v1/users/442")
        user = models.User(user_data.json())
        # Test attributes
        assert user.id_ == 442
        assert user.username == "hobbie"
        assert user.name == "A"
        assert user.is_sponsor is True
        assert user.location == "The Bayou"
        assert user.occupation == "numbers"
        assert user.about == "HOBBIE NEVER LEAVES, he just stops posting"
        assert user.sex == "m"
        assert user.display_title == "sup, yo"
        assert user.has_used_trial is False
        assert user.canonical_url == "https://roosterteeth.com/user/hobbie"
        assert user.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/57471ae3-ef5a-417f-9f48-8a82771a093c/tb/hobbie423534014eeb7.jpg"
        for quality in models.Thumbnail.qualities:
            assert user.get_thumbnail(quality) == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/57471ae3-ef5a-417f-9f48-8a82771a093c/{}/hobbie423534014eeb7.jpg".format(quality)

    def test_missing_all_thumbnail(self):
        with open(os.path.join(TEST_PREFIX, "missing_all_thumbnail_user.json"), "r") as resp:
            user_data = json.loads(resp.read())
            user = models.User(user_data)
            assert user.thumbnail is None
            for quality in models.Thumbnail.qualities:
                assert user.get_thumbnail(quality) is None

    def test_missing_single_thumbnail(self):
        with open(os.path.join(TEST_PREFIX, "missing_single_thumbnail_user.json"), "r") as resp:
            user_data = json.loads(resp.read())
            user = models.User(user_data)
            assert user.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/57471ae3-ef5a-417f-9f48-8a82771a093c/tb/hobbie423534014eeb7.jpg"
            assert user.get_thumbnail("sm") is None
