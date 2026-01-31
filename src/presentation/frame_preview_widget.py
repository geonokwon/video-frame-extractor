"""
프레임 미리보기 위젯
"""
from pathlib import Path
from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
    QLabel, QCheckBox, QLineEdit, QPushButton, QGridLayout,
    QFrame, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from src.domain.entities import VideoFrame


class FramePreviewItem(QFrame):
    """개별 프레임 미리보기 아이템"""
    
    selection_changed = Signal(int, bool)  # frame_number, selected
    caption_changed = Signal(int, str)  # frame_number, caption
    
    def __init__(self, frame: VideoFrame, parent=None):
        super().__init__(parent)
        self.frame = frame
        self.setObjectName("FrameCard")
        self.setCursor(Qt.PointingHandCursor)  # 클릭 가능 커서
        self._setup_ui()
        self._update_selection_style()
        
    def mousePressEvent(self, event):
        """카드 클릭 시 선택 토글"""
        if event.button() == Qt.LeftButton:
            self.frame.selected = not self.frame.selected
            self._update_selection_style()
            self.selection_changed.emit(self.frame.frame_number, self.frame.selected)
        super().mousePressEvent(event)
        
    def _setup_ui(self):
        """UI 구성"""
        # 메인 레이아웃 (세로)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 상단: 프레임명 - 타임스탬프
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # 프레임명
        frame_name_label = QLabel(f"프레임 {self.frame.frame_number}")
        frame_name_label.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        header_layout.addWidget(frame_name_label)
        
        # 구분자
        separator_label = QLabel("-")
        separator_label.setStyleSheet("color: #aaa;")
        header_layout.addWidget(separator_label)
        
        # 타임스탬프
        time_label = QLabel(f"⏱ {self._format_time(self.frame.timestamp)}")
        time_label.setStyleSheet("color: #aaa; font-size: 13px;")
        header_layout.addWidget(time_label)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # 하단: 이미지 | 장면설명
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)  # 기본 간격 제거
        
        # 중간: 썸네일 (영상 비율 유지)
        thumbnail_container = QWidget()
        thumbnail_layout = QVBoxLayout(thumbnail_container)
        thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setScaledContents(False)
        
        # 이미지 로드
        if self.frame.image_path.exists():
            pixmap = QPixmap(str(self.frame.image_path))
            
            # 원본 비율 계산
            img_width = pixmap.width()
            img_height = pixmap.height()
            
            # 최대 너비 250px 기준
            max_width = 250
            aspect_ratio = img_height / img_width if img_width > 0 else 1
            scaled_height = int(max_width * aspect_ratio)
            
            # 최대 높이 제한
            max_height = 350
            if scaled_height > max_height:
                scaled_height = max_height
                max_width = int(max_height / aspect_ratio)
            
            self.thumbnail_label.setFixedSize(max_width, scaled_height)
            scaled_pixmap = pixmap.scaled(
                max_width, scaled_height, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            self.thumbnail_label.setFixedSize(250, 200)
            self.thumbnail_label.setText("이미지 없음")
        
        thumbnail_layout.addWidget(self.thumbnail_label)
        content_layout.addWidget(thumbnail_container)
        
        # 이미지와 장면설명 사이 간격 (넓게)
        content_layout.addSpacing(20)
        
        # 오른쪽: 장면 설명 입력
        description_container = QWidget()
        description_layout = QVBoxLayout(description_container)
        description_layout.setContentsMargins(0, 0, 0, 0)
        description_layout.setSpacing(5)
        
        description_header = QLabel("장면 설명 (선택사항)")
        description_header.setStyleSheet("font-size: 13px; color: #bbb; font-weight: bold;")
        
        self.caption_input = QTextEdit()
        self.caption_input.setPlaceholderText("장면 설명을 입력하세요...\n(여러 줄 입력 가능)")
        self.caption_input.setText(self.frame.caption)
        self.caption_input.textChanged.connect(self._on_caption_changed)
        self.caption_input.setMinimumWidth(200)
        self.caption_input.setMinimumHeight(100)
        
        description_layout.addWidget(description_header)
        description_layout.addWidget(self.caption_input)
        description_layout.addStretch()
        
        content_layout.addWidget(description_container)
        
        main_layout.addLayout(content_layout)
        
    def _update_selection_style(self):
        """선택 상태에 따른 스타일 업데이트"""
        print(f"[DEBUG] 프레임 {self.frame.frame_number} 스타일 업데이트: selected={self.frame.selected}")
        
        if self.frame.selected:
            # 선택된 상태: 부드러운 초록색 테두리 (눈 덜 아프게)
            self.setStyleSheet("""
                QFrame#FrameCard {
                    background-color: #2b2b2b;
                    border: 4px solid #4CAF50;
                    border-radius: 8px;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 13px;
                }
                QLabel {
                    color: white;
                    border: none;
                    background: transparent;
                }
            """)
        else:
            # 선택 안된 상태: 회색 테두리
            self.setStyleSheet("""
                QFrame#FrameCard {
                    background-color: #2b2b2b;
                    border: 2px solid #3a3a3a;
                    border-radius: 8px;
                }
                QFrame#FrameCard:hover {
                    border: 2px solid #555;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 13px;
                }
                QLabel {
                    color: white;
                    border: none;
                    background: transparent;
                }
            """)
        
    def _format_time(self, seconds: float) -> str:
        """시간 포맷팅"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:05.2f}"
        
    def _on_caption_changed(self):
        """장면설명 변경"""
        text = self.caption_input.toPlainText()
        self.frame.caption = text
        self.caption_changed.emit(self.frame.frame_number, text)


class FramePreviewWidget(QWidget):
    """프레임 미리보기 그리드 위젯"""
    
    frames_updated = Signal(list)  # List[VideoFrame]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames: List[VideoFrame] = []
        self.preview_items: Dict[int, FramePreviewItem] = {}
        self._setup_ui()
        
    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # 그리드 컨테이너
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)
        
    def set_frames(self, frames: List[VideoFrame]):
        """프레임 목록 설정"""
        self.frames = frames
        self._refresh_grid()
        
    def _refresh_grid(self):
        """그리드 새로고침"""
        # 기존 아이템 제거
        for item in self.preview_items.values():
            item.deleteLater()
        self.preview_items.clear()
        
        # 그리드로 나열 (한 줄에 3개씩)
        columns = 3
        for i, frame in enumerate(self.frames):
            row = i // columns
            col = i % columns
            
            item = FramePreviewItem(frame)
            item.selection_changed.connect(self._on_frame_selection_changed)
            item.caption_changed.connect(self._on_frame_caption_changed)
            
            self.grid_layout.addWidget(item, row, col)
            self.preview_items[frame.frame_number] = item
            
    def _on_frame_selection_changed(self, frame_number: int, selected: bool):
        """프레임 선택 변경"""
        self.frames_updated.emit(self.frames)
        
    def _on_frame_caption_changed(self, frame_number: int, caption: str):
        """프레임 캡션 변경"""
        self.frames_updated.emit(self.frames)
        
    def get_selected_frames(self) -> List[VideoFrame]:
        """선택된 프레임 목록 반환"""
        selected = [f for f in self.frames if f.selected]
        print(f"[DEBUG] 선택된 프레임 수: {len(selected)}")
        for f in selected:
            print(f"[DEBUG] 프레임 {f.frame_number}: selected={f.selected}")
        return selected
    
    def select_all(self):
        """전체 선택"""
        for frame in self.frames:
            frame.selected = True
        # UI 아이템 스타일 업데이트
        for item in self.preview_items.values():
            item._update_selection_style()
        
    def deselect_all(self):
        """전체 선택 해제"""
        for frame in self.frames:
            frame.selected = False
        # UI 아이템 스타일 업데이트
        for item in self.preview_items.values():
            item._update_selection_style()
