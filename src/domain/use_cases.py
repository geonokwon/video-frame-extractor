"""
Domain Use Cases - 비즈니스 로직
"""
from pathlib import Path
from typing import List
from .entities import VideoFrame, VideoInfo, ExtractionConfig
from .repositories import IVideoRepository


class ExtractVideoFramesUseCase:
    """영상에서 프레임을 추출하는 Use Case"""
    
    def __init__(self, video_repository: IVideoRepository):
        self._repository = video_repository
    
    def execute(
        self, 
        video_path: Path, 
        config: ExtractionConfig
    ) -> List[VideoFrame]:
        """
        영상에서 프레임을 추출합니다.
        
        Args:
            video_path: 영상 파일 경로
            config: 추출 설정
            
        Returns:
            추출된 프레임 목록
            
        Raises:
            FileNotFoundError: 영상 파일이 없는 경우
            ValueError: 영상 파일이 유효하지 않은 경우
        """
        # 파일 존재 확인
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # 영상 파일 유효성 검사
        if not self._repository.validate_video_file(video_path):
            raise ValueError(f"Invalid video file: {video_path}")
        
        # 출력 디렉토리 생성
        config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 프레임 추출
        frames = self._repository.extract_frames(video_path, config)
        
        return frames


class GetVideoInfoUseCase:
    """영상 정보를 가져오는 Use Case"""
    
    def __init__(self, video_repository: IVideoRepository):
        self._repository = video_repository
    
    def execute(self, video_path: Path) -> VideoInfo:
        """
        영상 파일의 메타데이터를 가져옵니다.
        
        Args:
            video_path: 영상 파일 경로
            
        Returns:
            영상 정보
            
        Raises:
            FileNotFoundError: 영상 파일이 없는 경우
            ValueError: 영상 파일이 유효하지 않은 경우
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not self._repository.validate_video_file(video_path):
            raise ValueError(f"Invalid video file: {video_path}")
        
        return self._repository.get_video_info(video_path)
