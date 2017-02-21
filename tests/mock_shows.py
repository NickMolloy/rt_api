import os

from httmock import HTTMock, all_requests

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/show")


@all_requests
def regular_show_response(url, request):
    with open(os.path.join(TEST_PREFIX, "regular_show.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_name_show_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_name_show.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_cover_picture_show_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_cover_picture_show.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_all_thumbnail_show_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_all_thumbnail_show.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}
