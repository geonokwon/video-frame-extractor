# 🎬 영상 프레임 추출기

영상을 시간 간격에 따라 이미지로 자동 추출하는 macOS/Windows 앱

## ✨ 주요 기능

- 영상을 설정된 시간 간격으로 프레임 추출
- 다크 테마 UI
- 한글/일본어 파일명 지원
- FFmpeg 내장 (별도 설치 불필요)

## 🚀 빠른 시작

### 1. 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# FFmpeg 다운로드 (자동)
python scripts/download_ffmpeg.py
```

### 2. 실행

```bash
# GUI 실행
python run_gui.py

# 독립 실행 파일 빌드
python scripts/build_standalone.py
open dist/영상프레임추출기.app
```

## 📖 사용 방법

### 1단계: 영상 설정
1. **파일 선택**: 추출할 영상 파일 선택
2. **폴더 선택**: 저장할 출력 폴더 (선택사항, 기본: `./frames_selected`)
3. **설정 조정**:
   - 시간 간격: 1초마다 프레임 추출 (권장)
   - 이미지 포맷: PNG (고품질) 또는 JPG (작은 용량)
4. **미리보기 생성**: "🎬 프레임 미리보기 생성" 버튼 클릭

### 2단계: 프레임 선택 및 캡션 입력
1. **프레임 선택**: 체크박스로 원하는 프레임 선택
   - ✓ 전체 선택 / ✗ 전체 해제 버튼 사용 가능
2. **캡션 입력**: 각 프레임에 캡션 입력 (선택사항)
   - 캡션이 있는 프레임은 이미지 하단에 흰 여백과 텍스트 추가
3. **최종 저장**: "💾 선택한 프레임 저장" 버튼 클릭

### 3단계: 결과 확인
- "📂 결과 폴더 열기" 버튼으로 저장된 이미지 확인
- 캡션이 있는 프레임은 `frame_XXXX_caption.png` 형식으로 저장

## 📦 프로젝트 구조

```
영상분할기/
├── src/
│   ├── domain/          # 비즈니스 로직
│   ├── infrastructure/  # FFmpeg 구현
│   └── presentation/    # GUI
├── scripts/             # 빌드 스크립트
├── tests/               # 테스트
├── run_gui.py          # 앱 실행
└── requirements.txt    # 의존성
```

## 🛠️ 기술 스택

- **Python 3.13+**
- **PySide6** (Qt GUI)
- **FFmpeg** (영상 처리)
- **PyInstaller** (독립 실행 파일)

## ⚠️ macOS 보안 경고 해결

첫 실행 시 보안 경고가 나타나면:

```bash
# 보안 속성 제거
xattr -cr dist/영상프레임추출기.app

# 또는 우클릭 → "열기"
```

## 📄 라이선스

MIT License
