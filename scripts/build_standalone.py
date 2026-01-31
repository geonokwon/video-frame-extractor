#!/usr/bin/env python3
"""
독립 실행 파일 빌드 (FFmpeg 포함)
사용자가 아무것도 설치할 필요 없는 완전한 설치 패키지 생성
"""
import sys
import subprocess
import platform
import shutil
from pathlib import Path


APP_NAME = "영상프레임추출기"
SCRIPT_NAME = "run_gui.py"


def check_ffmpeg_binaries():
    """FFmpeg 바이너리 확인"""
    # 프로젝트 루트로 이동
    project_root = Path(__file__).parent.parent
    ffmpeg_dir = project_root / "ffmpeg_binaries"
    system = platform.system()
    exe_ext = ".exe" if system == "Windows" else ""
    
    ffmpeg_path = ffmpeg_dir / f"ffmpeg{exe_ext}"
    ffprobe_path = ffmpeg_dir / f"ffprobe{exe_ext}"
    
    if not ffmpeg_path.exists() or not ffprobe_path.exists():
        print("❌ FFmpeg 바이너리를 찾을 수 없습니다!")
        print(f"   찾은 위치: {ffmpeg_dir}")
        print("\n먼저 다음 명령을 실행하세요:")
        print("   python download_ffmpeg.py")
        return False
    
    print(f"✅ FFmpeg 바이너리 확인:")
    print(f"   - {ffmpeg_path}")
    print(f"   - {ffprobe_path}")
    return True


def build_standalone():
    """독립 실행 파일 빌드"""
    print("="*60)
    print("🔨 독립 실행 파일 빌드 (FFmpeg 포함)")
    print("="*60)
    print(f"\n플랫폼: {platform.system()} ({platform.machine()})")
    
    # FFmpeg 바이너리 확인
    if not check_ffmpeg_binaries():
        return 1
    
    # FFmpeg 경로
    project_root = Path(__file__).parent.parent
    ffmpeg_dir = project_root / "ffmpeg_binaries"
    system = platform.system()
    exe_ext = ".exe" if system == "Windows" else ""
    
    ffmpeg_binary = str(ffmpeg_dir / f"ffmpeg{exe_ext}")
    ffprobe_binary = str(ffmpeg_dir / f"ffprobe{exe_ext}")
    
    # PyInstaller 명령 구성
    # macOS .app 번들에서는 --onedir 사용 (--onefile과 충돌)
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # GUI 모드 (.app 생성)
        "--onedir",    # 폴더 모드 (macOS .app 번들용)
        "--clean",     # 빌드 전 정리
        "--noconfirm", # 덮어쓰기 확인 안 함
        
        # FFmpeg 바이너리 포함 (bin 폴더에 넣어서 이름 충돌 방지)
        "--add-binary", f"{ffmpeg_binary}:bin",
        "--add-binary", f"{ffprobe_binary}:bin",
        
        # Hidden imports
        "--hidden-import", "PySide6",
        "--hidden-import", "ffmpeg",
        "--hidden-import", "PIL",
        "--hidden-import", "src.domain.entities",
        "--hidden-import", "src.domain.use_cases",
        "--hidden-import", "src.domain.repositories",
        "--hidden-import", "src.infrastructure.ffmpeg_video_repository",
        "--hidden-import", "src.infrastructure.bundled_ffmpeg",
        "--hidden-import", "src.presentation.gui_qt",
        
        # 데이터 파일 제외
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "scipy",
        
        SCRIPT_NAME
    ]
    
    # 아이콘 추가 (있는 경우)
    icon_path = Path("icon.icns" if system == "Darwin" else "icon.ico")
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    
    print("\n📦 빌드 시작...")
    print(f"실행 명령: {' '.join(cmd)}\n")
    
    try:
        # PyInstaller 실행
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "="*60)
        print("✅ 빌드 완료!")
        print("="*60)
        
        # 결과 안내
        if system == "Darwin":
            print(f"\n🍎 macOS 앱: dist/{APP_NAME}.app")
            print("   ✓ FFmpeg 포함됨 (별도 설치 불필요)")
            print("   ✓ 더블클릭으로 실행 가능")
            print("\n📦 배포 방법:")
            print("   1. Applications 폴더로 복사")
            print("   2. 또는 DMG 생성:")
            print(f"      hdiutil create -volname '{APP_NAME}' \\")
            print(f"              -srcfolder dist/{APP_NAME}.app \\")
            print(f"              -ov -format UDZO {APP_NAME}.dmg")
            
        elif system == "Windows":
            print(f"\n💻 Windows 실행 파일: dist/{APP_NAME}.exe")
            print("   ✓ FFmpeg 포함됨 (별도 설치 불필요)")
            print("   ✓ 더블클릭으로 실행 가능")
            print("\n📦 배포 방법:")
            print("   1. 실행 파일 공유")
            print("   2. 또는 인스톨러 생성 (Inno Setup, NSIS)")
            
        else:
            print(f"\n🐧 Linux 실행 파일: dist/{APP_NAME}")
            print("   ✓ FFmpeg 포함됨 (별도 설치 불필요)")
            print(f"   ✓ ./dist/{APP_NAME} 로 실행")
        
        print("\n⚠️  참고:")
        print("   - 첫 실행 시 보안 경고가 나타날 수 있습니다")
        print("   - macOS: 시스템 환경설정에서 허용")
        print("   - Windows: '추가 정보' → '실행'")
        
        # 파일 크기 확인
        if system == "Darwin":
            app_path = Path("dist") / f"{APP_NAME}.app"
            if app_path.exists():
                size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
                print(f"\n📊 앱 크기: {size / (1024*1024):.1f} MB")
        else:
            exe_path = Path("dist") / f"{APP_NAME}{exe_ext}"
            if exe_path.exists():
                size = exe_path.stat().st_size
                print(f"\n📊 실행 파일 크기: {size / (1024*1024):.1f} MB")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 빌드 실패: {e}")
        return 1
    except FileNotFoundError:
        print("\n❌ PyInstaller가 설치되지 않았습니다.")
        print("   설치: pip install pyinstaller")
        return 1


if __name__ == '__main__':
    sys.exit(build_standalone())
