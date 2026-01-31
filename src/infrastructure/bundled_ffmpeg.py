"""
번들된 FFmpeg 경로 관리
PyInstaller로 패키징된 앱에서 FFmpeg 바이너리를 찾습니다
"""
import os
import sys
import platform
from pathlib import Path


def get_bundled_ffmpeg_path() -> str:
    """
    번들된 FFmpeg 실행 파일 경로를 반환합니다.
    
    Returns:
        FFmpeg 실행 파일의 절대 경로
        번들되지 않은 경우 시스템 FFmpeg 사용 ('ffmpeg')
    """
    # PyInstaller로 패키징된 경우
    if getattr(sys, 'frozen', False):
        exe_ext = '.exe' if platform.system() == 'Windows' else ''
        
        # 실행 파일이 있는 디렉토리
        if hasattr(sys, '_MEIPASS'):
            # --onefile 모드
            base_path = Path(sys._MEIPASS)
        else:
            # --onedir 모드 (macOS .app)
            # Contents/MacOS/영상프레임추출기 → Contents/Frameworks/bin/ffmpeg
            base_path = Path(sys.executable).parent.parent / 'Frameworks'
        
        # bin 폴더에서 찾기
        ffmpeg_path = base_path / 'bin' / f'ffmpeg{exe_ext}'
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
        
        # MacOS 폴더에서 찾기 (Windows 등)
        base_path = Path(sys.executable).parent
        ffmpeg_path = base_path / 'bin' / f'ffmpeg{exe_ext}'
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
        
        # 루트에서도 찾기
        ffmpeg_path = base_path / f'ffmpeg{exe_ext}'
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
    
    # 개발 모드에서는 다운로드된 바이너리 확인
    dev_ffmpeg = Path(__file__).parent.parent.parent / 'ffmpeg_binaries'
    exe_ext = '.exe' if platform.system() == 'Windows' else ''
    dev_ffmpeg_path = dev_ffmpeg / f'ffmpeg{exe_ext}'
    
    if dev_ffmpeg_path.exists():
        return str(dev_ffmpeg_path)
    
    # 시스템 FFmpeg 사용
    return 'ffmpeg'


def get_bundled_ffprobe_path() -> str:
    """
    번들된 FFprobe 실행 파일 경로를 반환합니다.
    
    Returns:
        FFprobe 실행 파일의 절대 경로
        번들되지 않은 경우 시스템 FFprobe 사용 ('ffprobe')
    """
    # PyInstaller로 패키징된 경우
    if getattr(sys, 'frozen', False):
        exe_ext = '.exe' if platform.system() == 'Windows' else ''
        
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            # --onedir 모드 (macOS .app)
            base_path = Path(sys.executable).parent.parent / 'Frameworks'
        
        # bin 폴더에서 찾기
        ffprobe_path = base_path / 'bin' / f'ffprobe{exe_ext}'
        if ffprobe_path.exists():
            return str(ffprobe_path)
        
        # MacOS 폴더에서 찾기
        base_path = Path(sys.executable).parent
        ffprobe_path = base_path / 'bin' / f'ffprobe{exe_ext}'
        if ffprobe_path.exists():
            return str(ffprobe_path)
        
        # 루트에서도 찾기
        ffprobe_path = base_path / f'ffprobe{exe_ext}'
        if ffprobe_path.exists():
            return str(ffprobe_path)
    
    # 개발 모드
    dev_ffmpeg = Path(__file__).parent.parent.parent / 'ffmpeg_binaries'
    exe_ext = '.exe' if platform.system() == 'Windows' else ''
    dev_ffprobe_path = dev_ffmpeg / f'ffprobe{exe_ext}'
    
    if dev_ffprobe_path.exists():
        return str(dev_ffprobe_path)
    
    return 'ffprobe'


def setup_ffmpeg_env():
    """
    FFmpeg 환경 변수 설정
    번들된 FFmpeg를 환경변수에 추가합니다
    """
    ffmpeg_path = get_bundled_ffmpeg_path()
    ffprobe_path = get_bundled_ffprobe_path()
    
    # 디버그 정보 출력
    print(f"[DEBUG] FFmpeg 경로: {ffmpeg_path}")
    print(f"[DEBUG] FFprobe 경로: {ffprobe_path}")
    print(f"[DEBUG] FFmpeg 존재: {os.path.exists(ffmpeg_path) if ffmpeg_path != 'ffmpeg' else '시스템 경로 사용'}")
    print(f"[DEBUG] FFprobe 존재: {os.path.exists(ffprobe_path) if ffprobe_path != 'ffprobe' else '시스템 경로 사용'}")
    
    # 환경변수에 경로 추가
    os.environ['FFMPEG_BINARY'] = ffmpeg_path
    os.environ['FFPROBE_BINARY'] = ffprobe_path
    
    return ffmpeg_path, ffprobe_path
