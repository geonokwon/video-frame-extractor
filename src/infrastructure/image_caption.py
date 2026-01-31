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
    font_size: int = 24,
    padding: int = 20,
    background_color: str = 'white',
    text_color: str = 'black',
    border_width: int = 3,
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
    font_paths = [
        # macOS 한글/일본어/영어 지원 폰트 (우선순위)
        '/System/Library/Fonts/AppleSDGothicNeo.ttc',  # 한글 + 영어 + 일본어
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',  # 유니코드 전체
        '/System/Library/Fonts/Hiragino Sans GB.ttc',  # 중국어 + 일본어
        '/System/Library/Fonts/Supplemental/Arial.ttf',  # 영어
    ]
    
    try:
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                header_font = ImageFont.truetype(font_path, 20)  # 헤더용 작은 폰트
                break
        if font is None:
            font = ImageFont.load_default()
            header_font = ImageFont.load_default()
    except Exception as e:
        print(f"[WARNING] 폰트 로드 실패: {e}")
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()
    
    # 상단 정보 바 높이
    header_height = 50
    
    # 캡션 텍스트 처리
    caption_height = 0
    lines = []
    
    if caption and caption.strip():
        # 임시 드로잉으로 텍스트 크기 측정
        temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        # 텍스트를 여러 줄로 분할 (너무 길면)
        words = caption.split(' ')
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
        
        # 전체 텍스트 높이 계산
        line_height = font_size + 8
        caption_height = len(lines) * line_height + 2 * padding
    
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
    
    # 프레임 번호 (왼쪽)
    frame_text = f"#{frame_number}"
    draw.text((border_width + 15, border_width + 15), frame_text, fill=text_color, font=header_font)
    
    # 타임스탬프 (오른쪽)
    if timestamp:
        bbox = draw.textbbox((0, 0), timestamp, font=header_font)
        timestamp_width = bbox[2] - bbox[0]
        draw.text(
            (total_width - border_width - timestamp_width - 15, border_width + 15),
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
    
    # 저장
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_img.save(output_path, quality=95)
    
    return output_path
