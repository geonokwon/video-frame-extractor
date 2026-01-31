# Windows용 설치파일 만들기

Windows 환경에서 설치 가능한 실행 파일(.exe)과 인스톨러를 만드는 가이드입니다.

## 📋 사전 준비

### 1. Windows 컴퓨터 필요
- macOS에서는 Windows용 빌드가 불가능합니다
- Windows 10/11 환경이 필요합니다

### 2. Python 설치
```bash
# https://www.python.org/ 에서 다운로드
# 설치 시 "Add Python to PATH" 체크!
```

### 3. 프로젝트 복사
```bash
# 프로젝트 폴더를 Windows 컴퓨터로 복사
# USB, 네트워크 공유, GitHub 등 사용
```

## 🔨 빌드 과정

### 단계 1: 환경 설정

```bash
# 명령 프롬프트(CMD) 또는 PowerShell 열기
cd 영상분할기

# 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
pip install pyinstaller
```

### 단계 2: FFmpeg 다운로드

```bash
# FFmpeg 바이너리 다운로드
python scripts\download_ffmpeg.py
```

### 단계 3: 실행 파일 빌드

```bash
# Windows 실행 파일 생성
python scripts\build_windows.py
```

**결과:** `dist/영상프레임추출기.exe` 파일 생성

이 파일 하나로 모든 것이 포함되어 있습니다:
- ✅ Python 런타임
- ✅ 모든 라이브러리 (PySide6, FFmpeg-Python, Pillow 등)
- ✅ FFmpeg/FFprobe 바이너리
- ✅ 소스 코드

### 단계 4: 인스톨러 생성 (선택사항)

더 전문적인 설치 경험을 제공하려면:

1. **Inno Setup 설치**
   - https://jrsoftware.org/isdl.php 방문
   - 다운로드 및 설치

2. **인스톨러 빌드**
   ```bash
   python scripts\build_windows_installer.py
   ```

**결과:** `scripts/installer_output/영상프레임추출기_Setup_v1.0.0.exe` 파일 생성

## 📦 배포

### 방법 1: 단일 실행 파일 배포

```
dist/영상프레임추출기.exe
```

- 👍 장점: 간단, 단일 파일
- 👎 단점: 파일 크기 큼 (~200MB)
- 사용법: 파일을 복사해서 더블클릭

### 방법 2: 인스톨러 배포

```
scripts/installer_output/영상프레임추출기_Setup_v1.0.0.exe
```

- 👍 장점: 전문적, 시작 메뉴 등록, 제거 프로그램
- 👎 단점: 추가 단계 필요
- 사용법: 인스톨러 실행 → 설치 → 시작 메뉴에서 실행

## ⚠️ 주의사항

### Windows Defender 경고

처음 실행 시 Windows Defender가 경고를 표시할 수 있습니다:

```
"Windows protected your PC"
```

**해결 방법:**
1. "More info" (추가 정보) 클릭
2. "Run anyway" (실행) 클릭

**근본 해결:**
- Code Signing Certificate 구매하여 서명
- 비용: ~$100-300/년

### 파일 크기

- 실행 파일: ~150-250MB
- 이유: Python 런타임 + 라이브러리 + FFmpeg 포함
- 정상입니다!

### 백신 프로그램

일부 백신 프로그램이 오탐지할 수 있습니다:
- PyInstaller로 만든 파일은 종종 오탐지됨
- 코드 서명으로 해결 가능

## 🧪 테스트

Windows 컴퓨터에서:

1. **실행 파일 테스트**
   ```bash
   dist\영상프레임추출기.exe
   ```

2. **모든 기능 테스트**
   - 영상 파일 선택
   - 프레임 추출
   - 캡션 입력
   - PDF 내보내기

3. **다른 Windows PC에서 테스트**
   - Python 없는 PC
   - FFmpeg 없는 PC
   - 깨끗한 환경

## 🐛 문제 해결

### "DLL not found" 에러

```bash
# Visual C++ Redistributable 설치 필요
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

### 실행 파일이 너무 큼

정상입니다. 다음이 모두 포함되어 있습니다:
- Python 런타임 (~50MB)
- Qt 라이브러리 (~100MB)
- FFmpeg (~50MB)

### 인스톨러 빌드 실패

```bash
# Inno Setup 경로 확인
dir "C:\Program Files (x86)\Inno Setup 6"

# 없으면 다시 설치
# https://jrsoftware.org/isdl.php
```

## 📚 추가 리소스

- [PyInstaller 문서](https://pyinstaller.org/)
- [Inno Setup 문서](https://jrsoftware.org/ishelp/)
- [Code Signing Guide](https://comodosslstore.com/code-signing)

## 💡 팁

1. **가상 머신 사용**
   - VirtualBox, VMware 등으로 Windows VM 생성
   - 깨끗한 환경에서 테스트

2. **GitHub Actions 사용**
   - Windows 환경에서 자동 빌드
   - CI/CD 파이프라인 구축

3. **버전 관리**
   - `installer.iss` 파일의 `MyAppVersion` 수정
   - 릴리스마다 버전 번호 증가
