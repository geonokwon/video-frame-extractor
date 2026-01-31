#!/usr/bin/env python3
"""
FFmpeg 바이너리 다운로드 스크립트
설치 파일에 FFmpeg를 포함시키기 위해 사용
"""
import sys
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path


def download_ffmpeg():
    """플랫폼에 맞는 FFmpeg 다운로드"""
    system = platform.system()
    machine = platform.machine()
    
    # FFmpeg 저장 디렉토리 (프로젝트 루트)
    project_root = Path(__file__).parent.parent
    ffmpeg_dir = project_root / "ffmpeg_binaries"
    ffmpeg_dir.mkdir(exist_ok=True)
    
    print(f"🔍 시스템: {system} ({machine})")
    print(f"📥 FFmpeg 다운로드 중...")
    
    if system == "Darwin":  # macOS
        download_ffmpeg_macos(ffmpeg_dir, machine)
    elif system == "Windows":
        download_ffmpeg_windows(ffmpeg_dir, machine)
    elif system == "Linux":
        download_ffmpeg_linux(ffmpeg_dir, machine)
    else:
        print(f"❌ 지원하지 않는 플랫폼: {system}")
        return False
    
    print("✅ FFmpeg 다운로드 완료!")
    return True


def download_ffmpeg_macos(ffmpeg_dir: Path, machine: str):
    """macOS용 FFmpeg 다운로드"""
    print("📦 macOS용 FFmpeg 다운로드...")
    
    # FFmpeg static build from https://evermeet.cx/ffmpeg/
    if machine == "arm64":
        url = "https://evermeet.cx/ffmpeg/ffmpeg-7.1.zip"
        probe_url = "https://evermeet.cx/ffmpeg/ffprobe-7.1.zip"
    else:
        url = "https://evermeet.cx/ffmpeg/ffmpeg-7.1.zip"
        probe_url = "https://evermeet.cx/ffmpeg/ffprobe-7.1.zip"
    
    # ffmpeg 다운로드
    print("  - ffmpeg 다운로드...")
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    urllib.request.urlretrieve(url, zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(ffmpeg_dir)
    zip_path.unlink()
    
    # ffprobe 다운로드
    print("  - ffprobe 다운로드...")
    probe_zip = ffmpeg_dir / "ffprobe.zip"
    urllib.request.urlretrieve(probe_url, probe_zip)
    
    with zipfile.ZipFile(probe_zip, 'r') as zip_ref:
        zip_ref.extractall(ffmpeg_dir)
    probe_zip.unlink()
    
    # 실행 권한 부여
    (ffmpeg_dir / "ffmpeg").chmod(0o755)
    (ffmpeg_dir / "ffprobe").chmod(0o755)
    
    print(f"  ✓ 저장 위치: {ffmpeg_dir}")


def download_ffmpeg_windows(ffmpeg_dir: Path, machine: str):
    """Windows용 FFmpeg 다운로드"""
    print("📦 Windows용 FFmpeg 다운로드...")
    
    # FFmpeg static build from https://github.com/BtbN/FFmpeg-Builds/releases
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    print("  - 다운로드 중... (약 100MB, 시간이 걸릴 수 있습니다)")
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    urllib.request.urlretrieve(url, zip_path)
    
    print("  - 압축 해제 중...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(ffmpeg_dir)
    zip_path.unlink()
    
    # bin 폴더에서 ffmpeg.exe, ffprobe.exe 찾아서 상위로 이동
    for root, dirs, files in (ffmpeg_dir).rglob("*"):
        if root.name == "bin":
            for file in ["ffmpeg.exe", "ffprobe.exe"]:
                src = root / file
                if src.exists():
                    shutil.copy2(src, ffmpeg_dir / file)
    
    # 압축 해제된 폴더 삭제
    for item in ffmpeg_dir.iterdir():
        if item.is_dir() and item.name.startswith("ffmpeg-"):
            shutil.rmtree(item)
    
    print(f"  ✓ 저장 위치: {ffmpeg_dir}")


def download_ffmpeg_linux(ffmpeg_dir: Path, machine: str):
    """Linux용 FFmpeg 다운로드"""
    print("📦 Linux용 FFmpeg 다운로드...")
    
    # FFmpeg static build
    if machine == "x86_64":
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    elif machine in ["aarch64", "arm64"]:
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
    else:
        print(f"  ⚠️  {machine} 아키텍처는 시스템 FFmpeg를 사용하세요")
        return
    
    print("  - 다운로드 중...")
    tar_path = ffmpeg_dir / "ffmpeg.tar.xz"
    urllib.request.urlretrieve(url, tar_path)
    
    print("  - 압축 해제 중...")
    with tarfile.open(tar_path, 'r:xz') as tar_ref:
        tar_ref.extractall(ffmpeg_dir)
    tar_path.unlink()
    
    # ffmpeg, ffprobe 찾아서 상위로 이동
    for root, dirs, files in ffmpeg_dir.rglob("*"):
        for file in ["ffmpeg", "ffprobe"]:
            src = Path(root) / file
            if src.exists() and src.is_file():
                dest = ffmpeg_dir / file
                shutil.copy2(src, dest)
                dest.chmod(0o755)
    
    # 압축 해제된 폴더 삭제
    for item in ffmpeg_dir.iterdir():
        if item.is_dir() and item.name.startswith("ffmpeg-"):
            shutil.rmtree(item)
    
    print(f"  ✓ 저장 위치: {ffmpeg_dir}")


def verify_ffmpeg():
    """다운로드된 FFmpeg 확인"""
    project_root = Path(__file__).parent.parent
    ffmpeg_dir = project_root / "ffmpeg_binaries"
    
    system = platform.system()
    exe_ext = ".exe" if system == "Windows" else ""
    
    ffmpeg_path = ffmpeg_dir / f"ffmpeg{exe_ext}"
    ffprobe_path = ffmpeg_dir / f"ffprobe{exe_ext}"
    
    if ffmpeg_path.exists() and ffprobe_path.exists():
        print(f"\n✅ FFmpeg 바이너리 준비 완료:")
        print(f"   - ffmpeg: {ffmpeg_path}")
        print(f"   - ffprobe: {ffprobe_path}")
        return True
    else:
        print(f"\n❌ FFmpeg 바이너리를 찾을 수 없습니다")
        return False


if __name__ == '__main__':
    try:
        if download_ffmpeg():
            verify_ffmpeg()
            print("\n📦 이제 build_standalone.py를 실행하세요!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
