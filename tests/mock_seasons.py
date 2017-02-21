import os

from httmock import HTTMock, all_requests

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/season")


@all_requests
def regular_season_response(url, request):
    with open(os.path.join(TEST_PREFIX, "regular_season.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_title_season_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_title_season.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}
