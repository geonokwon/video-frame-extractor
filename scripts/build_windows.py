#!/usr/bin/env python3
"""
Windows용 독립 실행 파일 빌드 (FFmpeg 포함)
Windows 환경에서 실행해야 합니다.
"""
import sys
import subprocess
import platform
import shutil
from pathlib import Path


APP_NAME = "영상프레임추출기"
SCRIPT_NAME = "run_gui.py"


def check_platform():
    """플랫폼 확인"""
    if platform.system() != "Windows":
        print("❌ 이 스크립트는 Windows에서만 실행할 수 있습니다.")
        print(f"   현재 플랫폼: {platform.system()}")
        print("\n💡 Windows 컴퓨터에서 다음 단계를 실행하세요:")
        print("   1. 프로젝트 폴더를 Windows로 복사")
        print("   2. Python 설치 (https://www.python.org/)")
        print("   3. pip install -r requirements.txt")
        print("   4. python scripts/download_ffmpeg.py")
        print("   5. python scripts/build_windows.py")
        return False
    return True


def check_ffmpeg_binaries():
    """FFmpeg 바이너리 확인"""
    project_root = Path(__file__).parent.parent
    ffmpeg_dir = project_root / "ffmpeg_binaries"
    
    ffmpeg_path = ffmpeg_dir / "ffmpeg.exe"
    ffprobe_path = ffmpeg_dir / "ffprobe.exe"
    
    if not ffmpeg_path.exists() or not ffprobe_path.exists():
        print("❌ FFmpeg 바이너리를 찾을 수 없습니다!")
        print(f"   찾은 위치: {ffmpeg_dir}")
        print("\n먼저 다음 명령을 실행하세요:")
        print("   python scripts/download_ffmpeg.py")
        return False
    
    print(f"✅ FFmpeg 바이너리 확인:")
    print(f"   - {ffmpeg_path}")
    print(f"   - {ffprobe_path}")
    return True


def build_windows_exe():
    """Windows 실행 파일 빌드"""
    print("="*60)
    print("🔨 Windows 독립 실행 파일 빌드 (FFmpeg 포함)")
    print("="*60)
    print(f"\n플랫폼: {platform.system()} ({platform.machine()})")
    
    # 플랫폼 확인
    if not check_platform():
        return 1
    
    # FFmpeg 바이너리 확인
    if not check_ffmpeg_binaries():
        return 1
    
    # FFmpeg 경로
    project_root = Path(__file__).parent.parent
    ffmpeg_dir = project_root / "ffmpeg_binaries"
    
    ffmpeg_binary = str(ffmpeg_dir / "ffmpeg.exe")
    ffprobe_binary = str(ffmpeg_dir / "ffprobe.exe")
    
    # 기존 빌드 폴더 삭제
    print("\n🗑️  기존 빌드 폴더 정리...")
    for folder in ["build", "dist"]:
        folder_path = project_root / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"   ✓ {folder} 폴더 삭제")
    
    # PyInstaller 명령 구성
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # GUI 모드 (콘솔 창 숨김)
        "--onefile",   # 단일 실행 파일
        "--clean",     # 빌드 전 정리
        "--noconfirm", # 덮어쓰기 확인 안 함
        
        # FFmpeg 바이너리 포함
        "--add-binary", f"{ffmpeg_binary};bin",
        "--add-binary", f"{ffprobe_binary};bin",
        
        # Hidden imports
        "--hidden-import", "PySide6",
        "--hidden-import", "ffmpeg",
        "--hidden-import", "PIL",
        "--hidden-import", "src.domain.entities",
        "--hidden-import", "src.domain.use_cases",
        "--hidden-import", "src.domain.repositories",
        "--hidden-import", "src.infrastructure.ffmpeg_video_repository",
        "--hidden-import", "src.infrastructure.bundled_ffmpeg",
        "--hidden-import", "src.infrastructure.image_caption",
        "--hidden-import", "src.presentation.gui_qt",
        "--hidden-import", "src.presentation.frame_preview_widget",
        "--hidden-import", "src.presentation.themes",
        
        # 불필요한 모듈 제외
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "scipy",
        "--exclude-module", "tkinter",
        
        SCRIPT_NAME
    ]
    
    # 아이콘 추가 (있는 경우)
    icon_path = project_root / "icon.ico"
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    
    print("\n📦 빌드 시작...")
    print(f"실행 명령: {' '.join(cmd)}\n")
    
    try:
        # PyInstaller 실행
        result = subprocess.run(cmd, check=True, cwd=str(project_root))
        
        print("\n" + "="*60)
        print("✅ 빌드 완료!")
        print("="*60)
        
        # 결과 안내
        exe_path = project_root / "dist" / f"{APP_NAME}.exe"
        
        print(f"\n💻 Windows 실행 파일: {exe_path}")
        print("   ✓ FFmpeg 포함됨 (별도 설치 불필요)")
        print("   ✓ 더블클릭으로 실행 가능")
        
        # 파일 크기 확인
        if exe_path.exists():
            size = exe_path.stat().st_size
            print(f"\n📊 실행 파일 크기: {size / (1024*1024):.1f} MB")
        
        print("\n📦 배포 방법:")
        print("   1. dist 폴더의 .exe 파일만 공유")
        print("   2. 또는 인스톨러 생성:")
        print("      python scripts/build_windows_installer.py")
        
        print("\n⚠️  참고:")
        print("   - 첫 실행 시 Windows Defender 경고가 나타날 수 있습니다")
        print("   - '추가 정보' → '실행' 클릭")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 빌드 실패: {e}")
        return 1
    except FileNotFoundError:
        print("\n❌ PyInstaller가 설치되지 않았습니다.")
        print("   설치: pip install pyinstaller")
        return 1


if __name__ == '__main__':
    sys.exit(build_windows_exe())
