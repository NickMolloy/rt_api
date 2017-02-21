import requests
from httmock import HTTMock

import pytest
from rt_api import models

from .context import mock_episodes


@pytest.mark.mocktest
class TestEpisode(object):

    def test_regular_episode(self):
        with HTTMock(mock_episodes.regular_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            # Test attributes
            assert episode.id_ == 31020
            assert episode.is_sponsor_only is False
            assert episode.title == "Crytek SHUTS DOWN Studios"
            assert episode.number == 402
            assert episode.show_name == "Game News"
            assert episode.caption == "Dec 20, 2016"
            assert episode.description == "Remember last week we reported on all those Crytek employees who weren't being paid? Now Crytek is shuttering five studios entirely, right before the holidays... not that they'd been paying their devs anyway..."
            assert episode.is_watched is True
            assert episode.canonical_url == "http://roosterteeth.com/episode/the-know-game-news-season-1-crytek-shuts-down-studios"
            assert episode.length == 402
            assert episode.show_id == 77
            assert episode.season_id == 114
            assert episode.site == "theKnow"
            assert episode.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/c50badea-baa8-48c1-a2e3-09920504a27e/tb/24363-1482281001906-thumbnail.jpg"
            assert episode.get_thumbnail("lg") == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/c50badea-baa8-48c1-a2e3-09920504a27e/original/24363-1482281001906-thumbnail.jpg"
            # Test video
            assert episode.video
            assert set(episode.video.available_qualities) == set(['240P', '360P', '480P', '720P', '1080P'])
            assert '480P' in episode.video.available_qualities
            assert episode.video.get_quality() == "http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-720P.m3u8"
            assert episode.video.type == "cdn"
            assert episode.video.get_quality("360P") == "http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-360P.m3u8"
            # Test links
            assert len(episode.links) == 5
            assert episode.links[0].title == "Crytek's press release"
            assert episode.links[1].url == "https://www.reddit.com/r/legaladvice/comments/5hg94d/crytek_hasnt_paid_me_or_my_coworkers_for_almost_6/"
            # Test audio
            assert episode.audio is None

    def test_episode_with_audio(self):
        with HTTMock(mock_episodes.episode_with_audio_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            assert episode.audio.container == "mp3"
            assert episode.audio.url == "http://www.podtrac.com/pts/redirect.mp3/traffic.libsyn.com/rtpodcast/Rooster_Teeth_Podcast_413.mp3"

    def test_missing_title_episode(self):
        with HTTMock(mock_episodes.missing_title_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            assert episode.title is None

    def test_missing_all_thumbnail(self):
        with HTTMock(mock_episodes.missing_all_thumbnail_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            assert episode.get_thumbnail("lg") is None
            assert episode.thumbnail is None

    def test_missing_single_thumbnail(self):
        with HTTMock(mock_episodes.missing_single_thumbnail_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            assert episode.thumbnail == "http://s3.amazonaws.com/cdn.roosterteeth.com/uploads/images/c50badea-baa8-48c1-a2e3-09920504a27e/sm/24363-1482281001906-thumbnail.jpg"
            assert episode.get_thumbnail("tb") is None

    def test_missing_video(self):
        with HTTMock(mock_episodes.missing_video_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            assert not episode.video
            assert episode.video is None

    def test_get_invalid_video_quality(self):
        with HTTMock(mock_episodes.regular_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            video = episode.video.get_quality(quality="2160P")
            assert video is None

    def test_episode_without_api(self):
        """Test that correct exception thrown when episode doesn't have an api reference."""
        with HTTMock(mock_episodes.regular_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            with pytest.raises(NotImplementedError):
                episode.season

    def test_set_and_get_video_quality(self):
        with HTTMock(mock_episodes.regular_episode_response):
            episode_data = requests.get("https://roosterteeth.com/api/v1/episodes/31020")
            episode = models.Episode(episode_data.json())
            episode.video.set_selected_quality("480P")
            assert episode.video.get_quality() == "http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-480P.m3u8"
