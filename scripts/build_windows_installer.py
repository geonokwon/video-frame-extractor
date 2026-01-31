#!/usr/bin/env python3
"""
Windows 인스톨러 생성 (Inno Setup 사용)
Windows 환경에서 실행해야 합니다.

사전 요구사항:
1. python scripts/build_windows.py 실행 완료
2. Inno Setup 설치 (https://jrsoftware.org/isdl.php)
"""
import sys
import subprocess
import platform
from pathlib import Path


def check_platform():
    """플랫폼 확인"""
    if platform.system() != "Windows":
        print("❌ 이 스크립트는 Windows에서만 실행할 수 있습니다.")
        print(f"   현재 플랫폼: {platform.system()}")
        return False
    return True


def check_exe_file():
    """실행 파일 확인"""
    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "영상프레임추출기.exe"
    
    if not exe_path.exists():
        print("❌ 실행 파일을 찾을 수 없습니다!")
        print(f"   예상 위치: {exe_path}")
        print("\n먼저 다음 명령을 실행하세요:")
        print("   python scripts/build_windows.py")
        return False
    
    print(f"✅ 실행 파일 확인: {exe_path}")
    return True


def find_inno_setup():
    """Inno Setup 경로 찾기"""
    # 일반적인 설치 경로들
    possible_paths = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 5\ISCC.exe"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def build_installer():
    """인스톨러 빌드"""
    print("="*60)
    print("📦 Windows 인스톨러 생성 (Inno Setup)")
    print("="*60)
    print(f"\n플랫폼: {platform.system()} ({platform.machine()})")
    
    # 플랫폼 확인
    if not check_platform():
        return 1
    
    # 실행 파일 확인
    if not check_exe_file():
        return 1
    
    # Inno Setup 찾기
    iscc_path = find_inno_setup()
    if not iscc_path:
        print("\n❌ Inno Setup을 찾을 수 없습니다.")
        print("\n다운로드 및 설치:")
        print("   1. https://jrsoftware.org/isdl.php 방문")
        print("   2. Inno Setup 다운로드 및 설치")
        print("   3. 다시 이 스크립트 실행")
        return 1
    
    print(f"✅ Inno Setup 확인: {iscc_path}")
    
    # 스크립트 경로
    project_root = Path(__file__).parent.parent
    script_path = project_root / "scripts" / "installer.iss"
    
    if not script_path.exists():
        print(f"\n❌ Inno Setup 스크립트를 찾을 수 없습니다:")
        print(f"   {script_path}")
        return 1
    
    print(f"✅ 스크립트 확인: {script_path}")
    
    # 인스톨러 빌드
    print("\n🔨 인스톨러 빌드 시작...")
    
    try:
        cmd = [str(iscc_path), str(script_path)]
        result = subprocess.run(
            cmd,
            check=True,
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        print("\n" + "="*60)
        print("✅ 인스톨러 빌드 완료!")
        print("="*60)
        
        # 결과 안내
        output_dir = project_root / "scripts" / "installer_output"
        print(f"\n📦 인스톨러 위치: {output_dir}")
        
        if output_dir.exists():
            installers = list(output_dir.glob("*.exe"))
            if installers:
                for installer in installers:
                    size = installer.stat().st_size
                    print(f"\n   📄 {installer.name}")
                    print(f"      크기: {size / (1024*1024):.1f} MB")
        
        print("\n🚀 배포 방법:")
        print("   1. installer_output 폴더의 Setup.exe 파일을 배포")
        print("   2. 사용자는 Setup.exe를 실행하여 설치")
        print("   3. 설치 후 시작 메뉴 또는 바탕화면에서 실행")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 빌드 실패:")
        print(e.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(build_installer())
