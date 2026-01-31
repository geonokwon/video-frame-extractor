"""
Domain Repositories - 인터페이스 정의 (Dependency Inversion Principle)
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from .entities import VideoFrame, VideoInfo, ExtractionConfig


class IVideoRepository(ABC):
    """영상 처리를 위한 Repository 인터페이스"""
    
    @abstractmethod
    def get_video_info(self, video_path: Path) -> VideoInfo:
        """영상 파일의 메타데이터를 가져옵니다"""
        pass
    
    @abstractmethod
    def extract_frames(
        self, 
        video_path: Path, 
        config: ExtractionConfig
    ) -> List[VideoFrame]:
        """설정에 따라 프레임을 추출합니다"""
        pass
    
    @abstractmethod
    def validate_video_file(self, video_path: Path) -> bool:
        """영상 파일이 유효한지 확인합니다"""
        pass
