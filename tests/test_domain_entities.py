"""
Domain Entities 테스트
"""
import pytest
from pathlib import Path
from src.domain.entities import VideoFrame, VideoInfo, ExtractionConfig


class TestVideoFrame:
    def test_create_valid_frame(self):
        frame = VideoFrame(
            timestamp=1.5,
            frame_number=45,
            image_path=Path("output/frame_001.png")
        )
        assert frame.timestamp == 1.5
        assert frame.frame_number == 45
        assert frame.image_path == Path("output/frame_001.png")
    
    def test_negative_timestamp_raises_error(self):
        with pytest.raises(ValueError, match="Timestamp must be non-negative"):
            VideoFrame(
                timestamp=-1.0,
                frame_number=0,
                image_path=Path("output/frame.png")
            )
    
    def test_negative_frame_number_raises_error(self):
        with pytest.raises(ValueError, match="Frame number must be non-negative"):
            VideoFrame(
                timestamp=0.0,
                frame_number=-1,
                image_path=Path("output/frame.png")
            )


class TestVideoInfo:
    def test_create_valid_video_info(self):
        info = VideoInfo(
            path=Path("video.mp4"),
            duration=10.5,
            fps=30.0,
            width=1920,
            height=1080,
            total_frames=315
        )
        assert info.duration == 10.5
        assert info.fps == 30.0
        assert info.total_frames == 315
    
    def test_invalid_duration_raises_error(self):
        with pytest.raises(ValueError, match="Duration must be positive"):
            VideoInfo(
                path=Path("video.mp4"),
                duration=0,
                fps=30.0,
                width=1920,
                height=1080,
                total_frames=0
            )
    
    def test_invalid_fps_raises_error(self):
        with pytest.raises(ValueError, match="FPS must be positive"):
            VideoInfo(
                path=Path("video.mp4"),
                duration=10.0,
                fps=0,
                width=1920,
                height=1080,
                total_frames=300
            )


class TestExtractionConfig:
    def test_create_valid_config(self):
        config = ExtractionConfig(
            interval=1.0,
            output_dir=Path("output"),
            image_format="png",
            image_quality=95
        )
        assert config.interval == 1.0
        assert config.image_format == "png"
        assert config.image_quality == 95
    
    def test_invalid_interval_raises_error(self):
        with pytest.raises(ValueError, match="Interval must be positive"):
            ExtractionConfig(
                interval=0,
                output_dir=Path("output")
            )
    
    def test_invalid_quality_raises_error(self):
        with pytest.raises(ValueError, match="Image quality must be between"):
            ExtractionConfig(
                interval=1.0,
                output_dir=Path("output"),
                image_quality=150
            )
    
    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError, match="Image format must be"):
            ExtractionConfig(
                interval=1.0,
                output_dir=Path("output"),
                image_format="bmp"
            )
