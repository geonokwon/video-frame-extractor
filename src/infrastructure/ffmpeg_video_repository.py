"""
FFmpeg를 사용한 Video Repository 구현
"""
import ffmpeg
import json
import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.domain.repositories import IVideoRepository
from src.domain.entities import VideoFrame, VideoInfo, ExtractionConfig

# FFmpeg 경로 설정
def _setup_ffmpeg_paths():
    """FFmpeg와 FFprobe 경로를 환경변수에 설정"""
    # 시스템 FFmpeg 경로 찾기
    ffmpeg_path = shutil.which('ffmpeg')
    ffprobe_path = shutil.which('ffprobe')
    
    # Homebrew 경로도 확인
    if not ffmpeg_path:
        homebrew_paths = [
            '/opt/homebrew/bin/ffmpeg',
            '/usr/local/bin/ffmpeg'
        ]
        for path in homebrew_paths:
            if os.path.exists(path):
                ffmpeg_path = path
                ffprobe_path = path.replace('ffmpeg', 'ffprobe')
                break
    
    # 환경변수에 설정
    if ffmpeg_path:
        os.environ['FFMPEG_BINARY'] = ffmpeg_path
    if ffprobe_path:
        os.environ['FFPROBE_BINARY'] = ffprobe_path
    
    return ffmpeg_path, ffprobe_path

# FFmpeg 경로 초기화
_ffmpeg_path, _ffprobe_path = _setup_ffmpeg_paths()

# 번들된 FFmpeg 경로
_bundled_ffmpeg: Optional[str] = None
_bundled_ffprobe: Optional[str] = None

try:
    from .bundled_ffmpeg import setup_ffmpeg_env
    _bundled_ffmpeg, _bundled_ffprobe = setup_ffmpeg_env()
    print(f"[INFO] 번들 FFmpeg: {_bundled_ffmpeg}")
    print(f"[INFO] 번들 FFprobe: {_bundled_ffprobe}")
except ImportError as e:
    print(f"[WARN] 번들 FFmpeg 로드 실패: {e}")
except Exception as e:
    print(f"[ERROR] FFmpeg 설정 에러: {e}")


def _get_ffmpeg_cmd() -> str:
    """사용할 FFmpeg 명령 경로 반환"""
    if _bundled_ffmpeg and os.path.exists(_bundled_ffmpeg):
        return _bundled_ffmpeg
    if _ffmpeg_path:
        return _ffmpeg_path
    return 'ffmpeg'


def _get_ffprobe_cmd() -> str:
    """사용할 FFprobe 명령 경로 반환"""
    if _bundled_ffprobe and os.path.exists(_bundled_ffprobe):
        return _bundled_ffprobe
    if _ffprobe_path:
        return _ffprobe_path
    return 'ffprobe'


class FFmpegVideoRepository(IVideoRepository):
    """FFmpeg를 사용한 영상 처리 구현"""
    
    def validate_video_file(self, video_path: Path) -> bool:
        """
        영상 파일이 유효한지 확인합니다.
        
        Args:
            video_path: 검사할 영상 파일 경로
            
        Returns:
            유효하면 True, 아니면 False
        """
        try:
            # 파일 존재 확인
            if not video_path.exists():
                print(f"[ERROR] 파일이 존재하지 않음: {video_path}")
                return False
            
            # 절대 경로로 변환
            abs_path = str(video_path.resolve())
            
            # FFprobe 명령
            ffprobe_cmd = _get_ffprobe_cmd()
            print(f"[DEBUG] FFprobe 사용: {ffprobe_cmd}")
            
            # FFmpeg probe 실행
            probe = ffmpeg.probe(abs_path, cmd=ffprobe_cmd)
            
            # 비디오 스트림이 있는지 확인
            video_streams = [
                stream for stream in probe['streams'] 
                if stream['codec_type'] == 'video'
            ]
            return len(video_streams) > 0
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            print(f"[ERROR] FFmpeg 에러: {error_msg}")
            return False
        except (KeyError, FileNotFoundError) as e:
            print(f"[ERROR] 파일 처리 에러: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 예상치 못한 에러: {type(e).__name__}: {e}")
            return False
    
    def get_video_info(self, video_path: Path) -> VideoInfo:
        """
        영상 파일의 메타데이터를 가져옵니다.
        
        Args:
            video_path: 영상 파일 경로
            
        Returns:
            영상 정보
            
        Raises:
            ValueError: 영상 정보를 읽을 수 없는 경우
        """
        try:
            # 절대 경로로 변환
            abs_path = str(video_path.resolve())
            
            # FFprobe 명령
            ffprobe_cmd = _get_ffprobe_cmd()
            print(f"[DEBUG] get_video_info에서 FFprobe 사용: {ffprobe_cmd}")
            
            # FFmpeg probe 실행
            probe = ffmpeg.probe(abs_path, cmd=ffprobe_cmd)
            
            # 비디오 스트림 찾기
            video_stream = next(
                (stream for stream in probe['streams'] 
                 if stream['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                raise ValueError("영상 파일에 비디오 스트림이 없습니다")
            
            # FPS 계산
            fps_parts = video_stream['r_frame_rate'].split('/')
            fps = float(fps_parts[0]) / float(fps_parts[1])
            
            # Duration 가져오기
            duration = float(probe['format']['duration'])
            
            # 총 프레임 수 계산
            total_frames = int(duration * fps)
            
            return VideoInfo(
                path=video_path,
                duration=duration,
                fps=fps,
                width=int(video_stream['width']),
                height=int(video_stream['height']),
                total_frames=total_frames
            )
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            raise ValueError(f"FFmpeg 에러:\n경로: {video_path}\n에러: {error_msg}")
        except KeyError as e:
            raise ValueError(f"영상 메타데이터 누락: {e}\n일부 영상 포맷은 지원되지 않을 수 있습니다")
        except ValueError as e:
            raise ValueError(f"영상 정보 처리 실패: {e}")
        except Exception as e:
            raise ValueError(f"예상치 못한 에러 ({type(e).__name__}): {e}\n경로: {video_path}")
    
    def extract_frames(
        self, 
        video_path: Path, 
        config: ExtractionConfig
    ) -> List[VideoFrame]:
        """
        설정에 따라 프레임을 추출합니다.
        
        Args:
            video_path: 영상 파일 경로
            config: 추출 설정
            
        Returns:
            추출된 프레임 목록
            
        Raises:
            RuntimeError: 프레임 추출 실패
        """
        try:
            # 영상 정보 가져오기
            video_info = self.get_video_info(video_path)
            
            # 출력 파일 패턴 설정
            output_pattern = str(config.output_dir / f"frame_%04d.{config.image_format}")
            
            # FFmpeg 명령 구성
            abs_video_path = str(video_path.resolve())
            stream = ffmpeg.input(abs_video_path)
            
            # FPS 필터 적용
            target_fps = 1.0 / config.interval
            stream = stream.filter('fps', fps=target_fps)
            
            # 출력 설정
            output_args = {
                'format': 'image2',
                'start_number': 0
            }
            
            if config.image_format in ['jpg', 'jpeg']:
                output_args['q:v'] = int((100 - config.image_quality) / 10) + 2
            
            stream = ffmpeg.output(stream, output_pattern, **output_args)
            stream = ffmpeg.overwrite_output(stream)
            
            # FFmpeg 명령
            ffmpeg_cmd = _get_ffmpeg_cmd()
            print(f"[DEBUG] FFmpeg 사용: {ffmpeg_cmd}")
            
            # 실행
            ffmpeg.run(stream, cmd=ffmpeg_cmd, capture_stdout=True, capture_stderr=True, quiet=True)
            
            # 생성된 프레임 목록 구성
            frames = []
            frame_number = 0
            timestamp = 0.0
            
            while timestamp <= video_info.duration:
                frame_filename = f"frame_{frame_number:04d}.{config.image_format}"
                frame_path = config.output_dir / frame_filename
                
                if frame_path.exists():
                    frames.append(VideoFrame(
                        timestamp=timestamp,
                        frame_number=frame_number,
                        image_path=frame_path
                    ))
                else:
                    break
                
                timestamp += config.interval
                frame_number += 1
            
            return frames
            
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg error: {stderr}")
        except Exception as e:
            raise RuntimeError(f"Failed to extract frames: {e}")
