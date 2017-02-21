import requests
from httmock import HTTMock

import pytest
from rt_api import models

from .context import mock_users


@pytest.mark.mocktest
class TestUser(object):

    def test_regular_user(self):
        with HTTMock(mock_users.regular_user_response):
            user_data = requests.get("https://roosterteeth.com/api/v1/users/2269568")
            user = models.User(user_data.json())
            # Test attributes
            assert user.id_ == 2269568
            assert user.username == "johnSmith112"
            assert user.name == "John Smith"
            assert user.is_sponsor is False
            assert user.location == "Earth"
            assert user.occupation == "Accountant"
            assert user.about == "Blah blah blah"
            assert user.sex == "m"
            assert user.display_title == "Stuff here"
            assert user.has_used_trial is True
            assert user.canonical_url == "http://roosterteeth.com/user/johnSmith112"
            assert user.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/default/tb/user_profile_male.jpg"
            assert user.get_thumbnail("md") == "http://s3.amazonaws.com/cdn.roosterteeth.com/default/md/user_profile_male.jpg"

    def test_missing_all_thumbnail(self):
        with HTTMock(mock_users.missing_all_thumbnail_response):
            user_data = requests.get("https://roosterteeth.com/api/v1/users/2269568")
            user = models.User(user_data.json())
            assert user.thumbnail is None
            assert user.get_thumbnail("lg") is None

    def test_missing_single_thumbnail(self):
        with HTTMock(mock_users.missing_single_thumbnail_response):
            user_data = requests.get("https://roosterteeth.com/api/v1/users/2269568")
            user = models.User(user_data.json())
            assert user.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/default/tb/user_profile_male.jpg"
            assert user.get_thumbnail("sm") is None
