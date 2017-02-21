import pytest
from rt_api import models


# Todo use vcr
class TestVideo(object):

    def test_set_quality(self):
        video = models.Video("http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/index.m3u8", "cdn")
        video.set_selected_quality("240P")
        assert video.get_quality() == "http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/NewHLS-240P.m3u8"

    def test_setting_wrong_quality(self):
        video = models.Video("http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/ea6d7410-d237-426a-a383-4884d8188f6d/index.m3u8", "cdn")
        quality = video.get_quality()
        with pytest.raises(KeyError):
            video.set_selected_quality("BadQuality")
        # Check that chosen quality has not changed
        assert quality == video.get_quality()

    def test_get_non_existant_quality(self):
        video = models.Video("http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/a9075320-244d-4572-9628-19bc897c05b7/index.m3u8", "cdn")
        # In this video, the 360P variant is labelled as 480P
        assert video.get_quality() is not None
        assert video.get_quality(quality="360P") == "http://wpc.1765A.taucdn.net/801765A/video/uploads/videos/a9075320-244d-4572-9628-19bc897c05b7/480P.m3u8"
        assert video.get_quality(quality="480P") is None
