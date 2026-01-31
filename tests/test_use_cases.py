"""
Use Cases 테스트
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from src.domain.use_cases import ExtractVideoFramesUseCase, GetVideoInfoUseCase
from src.domain.entities import VideoFrame, VideoInfo, ExtractionConfig


class TestExtractVideoFramesUseCase:
    def test_execute_with_valid_video(self, tmp_path):
        # Arrange
        video_path = tmp_path / "test.mp4"
        video_path.touch()  # 빈 파일 생성
        
        output_dir = tmp_path / "output"
        config = ExtractionConfig(
            interval=1.0,
            output_dir=output_dir
        )
        
        mock_repo = Mock()
        mock_repo.validate_video_file.return_value = True
        mock_repo.extract_frames.return_value = [
            VideoFrame(0.0, 0, output_dir / "frame_0000.png"),
            VideoFrame(1.0, 30, output_dir / "frame_0001.png"),
        ]
        
        use_case = ExtractVideoFramesUseCase(mock_repo)
        
        # Act
        frames = use_case.execute(video_path, config)
        
        # Assert
        assert len(frames) == 2
        assert frames[0].timestamp == 0.0
        assert frames[1].timestamp == 1.0
        mock_repo.validate_video_file.assert_called_once_with(video_path)
        mock_repo.extract_frames.assert_called_once_with(video_path, config)
        assert output_dir.exists()
    
    def test_execute_with_nonexistent_file(self):
        # Arrange
        video_path = Path("nonexistent.mp4")
        config = ExtractionConfig(
            interval=1.0,
            output_dir=Path("output")
        )
        mock_repo = Mock()
        use_case = ExtractVideoFramesUseCase(mock_repo)
        
        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Video file not found"):
            use_case.execute(video_path, config)
    
    def test_execute_with_invalid_video(self, tmp_path):
        # Arrange
        video_path = tmp_path / "invalid.mp4"
        video_path.touch()
        
        config = ExtractionConfig(
            interval=1.0,
            output_dir=Path("output")
        )
        
        mock_repo = Mock()
        mock_repo.validate_video_file.return_value = False
        
        use_case = ExtractVideoFramesUseCase(mock_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid video file"):
            use_case.execute(video_path, config)


class TestGetVideoInfoUseCase:
    def test_execute_with_valid_video(self, tmp_path):
        # Arrange
        video_path = tmp_path / "test.mp4"
        video_path.touch()
        
        expected_info = VideoInfo(
            path=video_path,
            duration=10.0,
            fps=30.0,
            width=1920,
            height=1080,
            total_frames=300
        )
        
        mock_repo = Mock()
        mock_repo.validate_video_file.return_value = True
        mock_repo.get_video_info.return_value = expected_info
        
        use_case = GetVideoInfoUseCase(mock_repo)
        
        # Act
        info = use_case.execute(video_path)
        
        # Assert
        assert info == expected_info
        mock_repo.validate_video_file.assert_called_once_with(video_path)
        mock_repo.get_video_info.assert_called_once_with(video_path)
    
    def test_execute_with_nonexistent_file(self):
        # Arrange
        video_path = Path("nonexistent.mp4")
        mock_repo = Mock()
        use_case = GetVideoInfoUseCase(mock_repo)
        
        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Video file not found"):
            use_case.execute(video_path)
