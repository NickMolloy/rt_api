import json
import os

import pytest
import vcr

from rt_api import models

from .context import auth

TEST_PREFIX = os.path.join(os.path.dirname(__file__), "test_data/episode")


@pytest.mark.usefixtures("auth")
class TestEpisode(object):

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episodes/test_regular_episode.yaml')
    def test_regular_episode(self):
        episode_data = self.auth.get("https://roosterteeth.com/api/v1/episodes/31020")
        episode = models.Episode(episode_data.json())
        # Test attributes
        assert episode.id_ == 31020
        assert episode.is_sponsor_only is False
        assert episode.title == "Crytek SHUTS DOWN Studios"
        assert episode.number == 402
        assert episode.show_name == "Game News"
        assert episode.caption == "Dec 20, 2016"
        assert episode.description == "Remember last week we reported on all those Crytek employees who weren't being paid? Now Crytek is shuttering five studios entirely, right before the holidays... not that they'd been paying their devs anyway..."
        assert episode.is_watched is False
        assert episode.canonical_url == "https://roosterteeth.com/episode/the-know-game-news-season-1-crytek-shuts-down-studios"
        assert episode.length == 402
        assert episode.show_id == 77
        assert episode.season_id == 114
        assert episode.site == "theKnow"
        # Test thumbnails
        assert episode.thumbnail == "https://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/c50badea-baa8-48c1-a2e3-09920504a27e/tb/24363-1482281001906-thumbnail.jpg"
        for quality in models.Thumbnail.qualities:
            assert episode.get_thumbnail(
                quality) == "https://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/c50badea-baa8-48c1-a2e3-09920504a27e/{}/24363-1482281001906-thumbnail.jpg".format(quality)
        # Test video
        assert episode.video
        assert set(episode.video.available_qualities) == set(
            ['240P', '360P', '480P', '720P', '1080P'])
        assert '480P' in episode.video.available_qualities
        assert episode.video.get_quality(
        ) == "https://rtv2-video.roosterteeth.com/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-720P.m3u8"
        assert episode.video.type == "cdn"
        assert episode.video.get_quality(
            "360P") == "https://rtv2-video.roosterteeth.com/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-360P.m3u8"
        # Test links
        assert len(episode.links) == 5
        assert episode.links[0].title == "Crytek's press release"
        assert episode.links[1].url == "https://www.reddit.com/r/legaladvice/comments/5hg94d/crytek_hasnt_paid_me_or_my_coworkers_for_almost_6/"
        # Test audio
        assert episode.audio is None

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episodes/test_episode_with_audio.yaml')
    def test_episode_with_audio(self):
        episode_data = self.auth.get("https://roosterteeth.com/api/v1/episodes/31139")
        episode = models.Episode(episode_data.json())
        assert episode.audio.container == "mp3"
        assert episode.audio.url == "http://www.podtrac.com/pts/redirect.mp3/traffic.libsyn.com/rtpodcast/Rooster_Teeth_Podcast_413.mp3"

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episodes/test_regular_episode.yaml')
    def test_get_invalid_video_quality(self):
        episode_data = self.auth.get("https://roosterteeth.com/api/v1/episodes/31020")
        episode = models.Episode(episode_data.json())
        video = episode.video.get_quality(quality="2160P")
        assert video is None

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episodes/test_regular_episode.yaml')
    def test_episode_without_api(self):
        """Test that correct exception thrown when episode doesn't have an api reference."""
        episode_data = self.auth.get("https://roosterteeth.com/api/v1/episodes/31020")
        episode = models.Episode(episode_data.json())
        with pytest.raises(NotImplementedError):
            episode.season

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/episodes/test_regular_episode.yaml')
    def test_set_and_get_video_quality(self):
        episode_data = self.auth.get("https://roosterteeth.com/api/v1/episodes/31020")
        episode = models.Episode(episode_data.json())
        episode.video.set_selected_quality("480P")
        assert episode.video.get_quality(
        ) == "https://rtv2-video.roosterteeth.com/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-480P.m3u8"


class TestMalformedEpisode(object):
    def test_missing_title_episode(self):
        with open(os.path.join(TEST_PREFIX, "missing_title_episode.json"), "r") as resp:
            episode_data = json.loads(resp.read())
            episode = models.Episode(episode_data)
            assert episode.title is None

    def test_missing_all_thumbnail(self):
        """Test when an episode respsonse is completely missing profilePicture attribute, so has no thumbnails."""
        with open(os.path.join(TEST_PREFIX, "missing_all_thumbnail_episode.json"), "r") as resp:
            episode_data = json.loads(resp.read())
            episode = models.Episode(episode_data)
            assert episode.get_thumbnail("lg") is None
            assert episode.thumbnail is None

    def test_missing_video(self):
        with open(os.path.join(TEST_PREFIX, "missing_video_episode.json"), "r") as resp:
            episode_data = json.loads(resp.read())
            episode = models.Episode(episode_data)
            assert episode.video is None

    def test_missing_audio(self):
        with open(os.path.join(TEST_PREFIX, "missing_audio_episode.json"), "r") as resp:
            episode_data = json.loads(resp.read())
            episode = models.Episode(episode_data)
            assert episode.audio is None

    def test_missing_links(self):
        with open(os.path.join(TEST_PREFIX, "missing_links_episode.json"), "r") as resp:
            episode_data = json.loads(resp.read())
            episode = models.Episode(episode_data)
            assert episode.audio is None
