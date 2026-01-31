"""
Domain Entities - 비즈니스 핵심 객체
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VideoFrame:
    """추출된 영상 프레임을 나타내는 Entity"""
    timestamp: float  # 초 단위
    frame_number: int
    image_path: Path
    caption: str = ""  # 캡션 (선택사항)
    selected: bool = False  # 선택 여부
    
    def __post_init__(self):
        if self.timestamp < 0:
            raise ValueError("Timestamp must be non-negative")
        if self.frame_number < 0:
            raise ValueError("Frame number must be non-negative")


@dataclass(frozen=True)
class VideoInfo:
    """영상 파일의 메타데이터"""
    path: Path
    duration: float  # 초 단위
    fps: float
    width: int
    height: int
    total_frames: int
    
    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError("Duration must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive")


@dataclass(frozen=True)
class ExtractionConfig:
    """프레임 추출 설정"""
    interval: float  # 초 단위 (예: 1.0 = 1초마다)
    output_dir: Path
    image_format: str = "png"
    image_quality: int = 95  # 1-100
    
    def __post_init__(self):
        if self.interval <= 0:
            raise ValueError("Interval must be positive")
        if self.image_quality < 1 or self.image_quality > 100:
            raise ValueError("Image quality must be between 1 and 100")
        if self.image_format not in ["png", "jpg", "jpeg", "pdf"]:
            raise ValueError("Image format must be png, jpg, jpeg, or pdf")
