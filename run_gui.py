#!/usr/bin/env python3
"""
영상 프레임 추출기 GUI 실행 파일 (Qt)
더블클릭으로 실행 가능
크로스플랫폼: macOS, Windows, Linux
"""
import sys
from src.presentation.gui_qt import main

if __name__ == '__main__':
    try:
        # 다크 테마를 기본으로 설정 (영상 편집 도구 느낌)
        # 밝은 테마를 원하면 --light 옵션 추가
        if '--light' not in sys.argv and '--dark' not in sys.argv:
            sys.argv.append('--dark')
        
        main()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("엔터를 눌러 종료...")
        sys.exit(1)
