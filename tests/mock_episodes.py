import os

from httmock import HTTMock, all_requests

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/episode")


@all_requests
def regular_episode_response(url, request):
    with open(os.path.join(TEST_PREFIX, "regular_episode.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_title_episode_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_title_episode.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_all_thumbnail_episode_response(url, request):
    """Test when an episode respsonse is completely missing profilePicture attribute, so has no thumbnails."""
    with open(os.path.join(TEST_PREFIX, "missing_all_thumbnail_episode.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_single_thumbnail_episode_response(url, request):
    """Test when an episode respsonse is missing the default thumbnail size."""
    with open(os.path.join(TEST_PREFIX, "missing_single_thumbnail_episode.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def missing_video_episode_response(url, request):
    with open(os.path.join(TEST_PREFIX, "missing_video_episode.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}


@all_requests
def episode_with_audio_response(url, request):
    with open(os.path.join(TEST_PREFIX, "episode_with_audio.json"), "r") as resp:
        return {'status_code': 200, 'content': resp.read()}
