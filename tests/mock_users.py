import os

from httmock import HTTMock, all_requests

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/user")


@all_requests
def regular_user_response(url, request):
    with open(os.path.join(TEST_PREFIX, "regular_user.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_all_thumbnail_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_all_thumbnail_user.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_single_thumbnail_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_single_thumbnail_user.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}
