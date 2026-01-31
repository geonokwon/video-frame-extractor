"""
Command Line Interface
"""
import argparse
from pathlib import Path
import sys
from typing import Optional

from src.domain.entities import ExtractionConfig
from src.domain.use_cases import ExtractVideoFramesUseCase, GetVideoInfoUseCase
from src.infrastructure.ffmpeg_video_repository import FFmpegVideoRepository


class CLI:
    """커맨드 라인 인터페이스"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.repository = FFmpegVideoRepository()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """CLI argument parser를 생성합니다"""
        parser = argparse.ArgumentParser(
            description='영상을 프레임 단위로 분할하여 이미지로 저장합니다',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
예제:
  # 1초마다 프레임 추출
  python main.py extract video.mp4 -i 1.0 -o ./frames
  
  # 0.5초마다 JPG로 추출
  python main.py extract video.mp4 -i 0.5 -o ./frames -f jpg
  
  # 영상 정보 확인
  python main.py info video.mp4
            '''
        )
        
        subparsers = parser.add_subparsers(dest='command', help='사용할 명령')
        
        # extract 명령
        extract_parser = subparsers.add_parser(
            'extract',
            help='영상에서 프레임을 추출합니다'
        )
        extract_parser.add_argument(
            'video',
            type=str,
            help='입력 영상 파일 경로'
        )
        extract_parser.add_argument(
            '-i', '--interval',
            type=float,
            default=1.0,
            help='프레임 추출 간격 (초 단위, 기본값: 1.0)'
        )
        extract_parser.add_argument(
            '-o', '--output',
            type=str,
            default='./frames',
            help='출력 디렉토리 (기본값: ./frames)'
        )
        extract_parser.add_argument(
            '-f', '--format',
            type=str,
            choices=['png', 'jpg', 'jpeg'],
            default='png',
            help='출력 이미지 포맷 (기본값: png)'
        )
        extract_parser.add_argument(
            '-q', '--quality',
            type=int,
            default=95,
            help='이미지 품질 1-100 (기본값: 95, JPG에만 적용)'
        )
        
        # info 명령
        info_parser = subparsers.add_parser(
            'info',
            help='영상 파일의 정보를 출력합니다'
        )
        info_parser.add_argument(
            'video',
            type=str,
            help='입력 영상 파일 경로'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None):
        """CLI를 실행합니다"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == 'extract':
                return self._extract_command(parsed_args)
            elif parsed_args.command == 'info':
                return self._info_command(parsed_args)
        except Exception as e:
            print(f"❌ 에러: {e}", file=sys.stderr)
            return 1
    
    def _extract_command(self, args) -> int:
        """extract 명령을 실행합니다"""
        video_path = Path(args.video)
        output_dir = Path(args.output)
        
        print(f"📹 영상 파일: {video_path}")
        print(f"⏱️  추출 간격: {args.interval}초")
        print(f"📁 출력 디렉토리: {output_dir}")
        print(f"🖼️  이미지 포맷: {args.format}")
        print()
        
        # 설정 생성
        config = ExtractionConfig(
            interval=args.interval,
            output_dir=output_dir,
            image_format=args.format,
            image_quality=args.quality
        )
        
        # Use Case 실행
        use_case = ExtractVideoFramesUseCase(self.repository)
        
        print("🔄 프레임 추출 중...")
        frames = use_case.execute(video_path, config)
        
        print(f"✅ 완료! {len(frames)}개의 프레임을 추출했습니다.")
        print(f"📂 저장 위치: {output_dir}")
        
        # 처음 몇 개의 프레임 정보 출력
        if frames:
            print("\n📸 추출된 프레임 샘플:")
            for frame in frames[:5]:
                print(f"  - {frame.timestamp:.2f}초 → {frame.image_path.name}")
            if len(frames) > 5:
                print(f"  ... 외 {len(frames) - 5}개")
        
        return 0
    
    def _info_command(self, args) -> int:
        """info 명령을 실행합니다"""
        video_path = Path(args.video)
        
        # Use Case 실행
        use_case = GetVideoInfoUseCase(self.repository)
        info = use_case.execute(video_path)
        
        print(f"📹 영상 정보")
        print(f"{'=' * 50}")
        print(f"파일: {info.path.name}")
        print(f"길이: {info.duration:.2f}초 ({info.duration / 60:.1f}분)")
        print(f"FPS: {info.fps:.2f}")
        print(f"해상도: {info.width}x{info.height}")
        print(f"총 프레임: {info.total_frames:,}")
        print(f"{'=' * 50}")
        
        return 0


def main(args: Optional[list] = None) -> int:
    """메인 진입점"""
    cli = CLI()
    return cli.run(args)
