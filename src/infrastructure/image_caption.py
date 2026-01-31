"""
이미지에 장면 설명 추가 유틸리티
UTF-8 지원: 한글, 영어, 일본어, 중국어 등 모든 언어 지원
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


def add_caption_to_image(
    image_path: Path,
    output_path: Path,
    caption: str = "",
    frame_number: int = 0,
    timestamp: str = "",
    position: str = 'bottom',
    font_size: int = 60,  # 70 -> 60 (더 작게)
    padding: int = 18,  # 22 -> 18 (여백 줄임)
    background_color: str = 'white',
    text_color: str = 'black',
    border_width: int = 6,  # 8 -> 6 (테두리 줄임)
    border_color: str = 'black'
) -> Path:
    """
    이미지에 프레임 정보와 장면 설명을 추가합니다.
    
    Args:
        image_path: 원본 이미지 경로
        output_path: 출력 이미지 경로
        caption: 추가할 장면 설명 텍스트 (빈 문자열이면 캡션 없이 저장)
        frame_number: 프레임 번호 (왼쪽 상단에 표시)
        timestamp: 타임스탬프 (오른쪽 상단에 표시)
        position: 캡션 위치 ('top' 또는 'bottom')
        font_size: 글꼴 크기
        padding: 여백 크기
        background_color: 배경색
        text_color: 텍스트 색상
        border_width: 테두리 두께
        border_color: 테두리 색상
        
    Returns:
        출력 이미지 경로
    """
    
    # 이미지 열기
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    # 폰트 설정 (UTF-8 지원: 한글, 영어, 일본어, 중국어 등)
    font = None
    header_font = None
    
    # OS별 폰트 경로
    import platform
    system = platform.system()
    
    if system == "Windows":
        font_paths = [
            'C:/Windows/Fonts/malgun.ttf',  # 맑은 고딕 (한글)
            'C:/Windows/Fonts/gulim.ttc',   # 굴림 (한글)
            'C:/Windows/Fonts/batang.ttc',  # 바탕 (한글)
            'C:/Windows/Fonts/arial.ttf',   # Arial (영어)
        ]
    else:  # macOS
        font_paths = [
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',  # 한글 + 영어 + 일본어
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',  # 유니코드 전체
            '/System/Library/Fonts/Hiragino Sans GB.ttc',  # 중국어 + 일본어
            '/System/Library/Fonts/Supplemental/Arial.ttf',  # 영어
        ]
    
    try:
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                header_font = ImageFont.truetype(font_path, int(font_size * 0.75))  # 헤더 폰트 (60의 75% = 45)
                break
        if font is None:
            font = ImageFont.load_default()
            header_font = ImageFont.load_default()
    except Exception as e:
        print(f"[WARNING] 폰트 로드 실패: {e}")
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()
    
    # 상단 정보 바 높이 (폰트 크기에 비례, 여백 최소화)
    header_height = int(font_size * 1.3)  # 폰트가 72일 때 약 94px (여백 최소화)
    
    # 캡션 텍스트 처리
    caption_height = 0
    lines = []
    
    if caption and caption.strip():
        # 임시 드로잉으로 텍스트 크기 측정
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        # 줄바꿈 문자 먼저 처리
        caption_lines = caption.split('\n')
        
        # 각 줄에 대해 너비가 넘으면 추가 분할
        for line in caption_lines:
            if not line.strip():
                lines.append('')  # 빈 줄도 유지
                continue
                
            words = line.split(' ')
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = temp_draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= img_width - 2 * padding:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
        
        # 전체 텍스트 높이 계산 (더 넉넉하게)
        bbox = temp_draw.textbbox((0, 0), "Ay", font=font)  # 실제 폰트 높이 측정
        actual_font_height = bbox[3] - bbox[1]
        line_height = int(actual_font_height * 1.4)  # 줄 간격 1.4배
        caption_height = len(lines) * line_height + 2 * padding + int(padding * 0.5)  # 위아래 여유 공간
    
    # 새 이미지 생성 (헤더 + 원본 + 캡션 + 테두리)
    total_width = img_width + 2 * border_width
    total_height = header_height + img_height + caption_height + 2 * border_width
    
    # 배경 이미지 (테두리 색상)
    new_img = Image.new('RGB', (total_width, total_height), border_color)
    
    # 상단 헤더 (흰 배경)
    draw = ImageDraw.Draw(new_img)
    draw.rectangle(
        [(border_width, border_width), (total_width - border_width, header_height)],
        fill=background_color
    )
    
    # 프레임 번호 (왼쪽) - 상단에 최대한 가깝게
    frame_text = f"#{frame_number}"
    text_y_pos = border_width + int(padding * 0.3)  # 여백 더 줄임
    text_x_padding = int(padding * 0.4)
    draw.text((border_width + text_x_padding, text_y_pos), frame_text, fill=text_color, font=header_font)
    
    # 타임스탬프 (오른쪽) - 상단에 최대한 가깝게
    if timestamp:
        bbox = draw.textbbox((0, 0), timestamp, font=header_font)
        timestamp_width = bbox[2] - bbox[0]
        draw.text(
            (total_width - border_width - timestamp_width - text_x_padding, text_y_pos),
            timestamp,
            fill=text_color,
            font=header_font
        )
    
    # 원본 이미지 붙이기
    new_img.paste(img, (border_width, header_height + border_width))
    
    # 캡션 그리기 (있을 경우)
    if lines:
        caption_y_start = header_height + border_width + img_height
        
        # 캡션 배경 (흰색)
        draw.rectangle(
            [(border_width, caption_y_start), (total_width - border_width, total_height - border_width)],
            fill=background_color
        )
        
        # 캡션 텍스트
        line_height = font_size + 8
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (total_width - text_width) // 2  # 중앙 정렬
            text_y = caption_y_start + padding + i * line_height
            
            draw.text((text_x, text_y), line, fill=text_color, font=font)
    
    # 저장 (UTF-8 인코딩 보장)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Windows에서 한글 경로 처리
    import sys
    if sys.platform == 'win32':
        # Windows에서는 문자열로 변환하여 저장
        output_str = str(output_path)
        new_img.save(output_str, quality=95, optimize=True)
    else:
        new_img.save(output_path, quality=95, optimize=True)
    
    return output_path
