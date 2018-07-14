import pytest
import vcr

from rt_api import models


class TestVideo(object):

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/video/get_video.yaml')
    def test_set_quality(self):
        video = models.Video("https://rtv2-roosterteeth.akamaized.net/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/index.m3u8", "cdn")
        video.set_selected_quality("240P")
        assert video.get_quality() == "https://rtv2-roosterteeth.akamaized.net/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-240P.m3u8"

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/video/get_video.yaml')
    def test_setting_wrong_quality(self):
        video = models.Video("https://rtv2-roosterteeth.akamaized.net/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/index.m3u8", "cdn")
        quality = video.get_quality()
        with pytest.raises(KeyError):
            video.set_selected_quality("BadQuality")
        # Check that chosen quality has not changed
        assert quality == video.get_quality()

    @vcr.use_cassette('tests/fixtures/vcr_cassettes/video/get_video.yaml')
    def test_get_non_existant_quality(self):
        video = models.Video("https://rtv2-roosterteeth.akamaized.net/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/index.m3u8", "cdn")
        assert video.get_quality() is not None
        assert video.get_quality(quality="1080P") == "https://rtv2-roosterteeth.akamaized.net/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-1080P.m3u8"
        assert video.get_quality(quality="BadQuality") is None
