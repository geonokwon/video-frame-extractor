"""
Modern GUI Interface using PySide6 (Qt)
프레임 선택 및 캡션 기능 포함
"""
import sys
from pathlib import Path
from typing import Optional, List
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QComboBox, QProgressBar,
    QTextEdit, QFileDialog, QMessageBox, QGroupBox, QDoubleSpinBox,
    QSlider, QFrame, QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont

from src.domain.entities import ExtractionConfig, VideoFrame
from src.domain.use_cases import ExtractVideoFramesUseCase, GetVideoInfoUseCase
from src.infrastructure.ffmpeg_video_repository import FFmpegVideoRepository
from src.infrastructure.image_caption import add_caption_to_image
from src.presentation.frame_preview_widget import FramePreviewWidget
from src.presentation.themes import (
    LIGHT_THEME, DARK_THEME, 
    BUTTON_LIGHT, BUTTON_DARK,
    STATUS_LIGHT, STATUS_DARK,
    INFO_TEXT_LIGHT, INFO_TEXT_DARK,
    TITLE_LIGHT, TITLE_DARK
)


class ExtractionThread(QThread):
    """프레임 추출을 백그라운드에서 실행하는 스레드"""
    
    progress_updated = Signal(int)
    extraction_completed = Signal(list)  # List[VideoFrame]
    extraction_failed = Signal(str)
    
    def __init__(self, video_path: Path, config: ExtractionConfig):
        super().__init__()
        self.video_path = video_path
        self.config = config
        self.repository = FFmpegVideoRepository()
        
    def run(self):
        """스레드 실행"""
        try:
            use_case = ExtractVideoFramesUseCase(self.repository)
            self.progress_updated.emit(30)
            
            frames = use_case.execute(self.video_path, self.config)
            
            self.progress_updated.emit(100)
            self.extraction_completed.emit(frames)
            
        except Exception as e:
            self.extraction_failed.emit(str(e))


class SaveSelectedFramesThread(QThread):
    """선택된 프레임을 저장하는 스레드 (캡션 포함)"""
    
    progress_updated = Signal(int)
    save_completed = Signal(int)  # 저장된 프레임 수
    save_failed = Signal(str)
    
    def __init__(self, frames: List[VideoFrame], output_dir: Path, image_format: str):
        super().__init__()
        self.frames = frames
        self.output_dir = output_dir
        self.image_format = image_format
        
    def run(self):
        """스레드 실행"""
        try:
            saved_count = 0
            total = len(self.frames)
            
            # PDF인 경우: 모든 선택된 프레임을 하나의 PDF로 결합
            if self.image_format.lower() == 'pdf':
                from PIL import Image
                import tempfile
                
                # 임시 이미지 리스트
                temp_images = []
                pil_images = []
                
                # 선택된 프레임만 추출
                selected_frames = [f for f in self.frames if f.selected]
                
                for i, frame in enumerate(selected_frames):
                    # 선택된 순서로 번호 매기기 (1부터 시작)
                    sequence_number = i + 1
                    
                    # 타임스탬프 포맷팅
                    minutes = int(frame.timestamp // 60)
                    seconds = frame.timestamp % 60
                    timestamp_str = f"{minutes:02d}:{seconds:05.2f}"
                    
                    # 임시 이미지 생성
                    temp_path = self.output_dir / f"temp_frame_{sequence_number:04d}.png"
                    add_caption_to_image(
                        frame.image_path,
                        temp_path,
                        caption=frame.caption,
                        frame_number=sequence_number,  # 선택 순서로 변경
                        timestamp=timestamp_str,
                        position='bottom'
                    )
                    
                    # PIL 이미지로 로드
                    img = Image.open(temp_path)
                    # RGB 모드로 변환 (PDF는 RGBA 지원 안 함)
                    if img.mode == 'RGBA':
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                        pil_images.append(rgb_img)
                    else:
                        pil_images.append(img.convert('RGB'))
                    
                    temp_images.append(temp_path)
                    saved_count += 1
                    
                    # 진행률 업데이트
                    progress = int((i + 1) / total * 90)  # 90%까지만
                    self.progress_updated.emit(progress)
                
                # PDF 생성
                if pil_images:
                    pdf_path = self.output_dir / "frames_combined.pdf"
                    pil_images[0].save(
                        pdf_path,
                        save_all=True,
                        append_images=pil_images[1:] if len(pil_images) > 1 else [],
                        resolution=100.0,
                        quality=95
                    )
                    
                    # 임시 파일 삭제
                    for temp_path in temp_images:
                        if temp_path.exists():
                            temp_path.unlink()
                    
                    self.progress_updated.emit(100)
                
                self.save_completed.emit(saved_count)
            
            # 일반 이미지 포맷인 경우
            else:
                # 선택된 프레임만 추출
                selected_frames = [f for f in self.frames if f.selected]
                
                for i, frame in enumerate(selected_frames):
                    # 선택된 순서로 번호 매기기 (1부터 시작)
                    sequence_number = i + 1
                    
                    # 타임스탬프 포맷팅
                    minutes = int(frame.timestamp // 60)
                    seconds = frame.timestamp % 60
                    timestamp_str = f"{minutes:02d}:{seconds:05.2f}"
                    
                    # 파일명 결정 (선택 순서로)
                    if frame.caption:
                        output_path = self.output_dir / f"frame_{sequence_number:04d}_description.{self.image_format}"
                    else:
                        output_path = self.output_dir / f"frame_{sequence_number:04d}.{self.image_format}"
                    
                    # 이미지에 프레임 정보 추가 (선택 순서로 번호 매김)
                    add_caption_to_image(
                        frame.image_path,
                        output_path,
                        caption=frame.caption,
                        frame_number=sequence_number,  # 선택 순서로 변경
                        timestamp=timestamp_str,
                        position='bottom'
                    )
                    
                    saved_count += 1
                    
                    # 진행률 업데이트
                    progress = int((i + 1) / len(selected_frames) * 100)
                    self.progress_updated.emit(progress)
                
                self.save_completed.emit(saved_count)
            
        except Exception as e:
            self.save_failed.emit(str(e))


class VideoFrameExtractorQt(QMainWindow):
    """영상 프레임 추출기 GUI (Qt)"""
    
    def __init__(self, theme='dark'):
        super().__init__()
        
        self.setWindowTitle("🎬 영상 프레임 추출기")
        self.setMinimumSize(1200, 800)
        
        # Repository 초기화
        self.repository = FFmpegVideoRepository()
        
        # 테마 설정
        self.theme = theme
        
        # 변수 초기화
        self.video_path: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        self.temp_output_dir: Optional[Path] = None
        self.extracted_frames: List[VideoFrame] = []
        self.extraction_thread: Optional[ExtractionThread] = None
        self.save_thread: Optional[SaveSelectedFramesThread] = None
        
        # UI 구성
        self._setup_ui()
        self._apply_styles()
        
    def _setup_ui(self):
        """UI 구성"""
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 타이틀
        title_label = QLabel("🎬 영상 프레임 추출기")
        title_font = QFont("Helvetica", 28, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(TITLE_LIGHT if self.theme == 'light' else TITLE_DARK)
        main_layout.addWidget(title_label)
        
        # 구분선
        main_layout.addWidget(self._create_separator())
        
        # 스택 위젯 (2단계 화면)
        self.stack = QStackedWidget()
        
        # Stage 1: 설정 화면
        self.setup_page = self._create_setup_page()
        self.stack.addWidget(self.setup_page)
        
        # Stage 2: 프레임 선택 화면
        self.preview_page = self._create_preview_page()
        self.stack.addWidget(self.preview_page)
        
        main_layout.addWidget(self.stack)
        
        # 상태 바
        self.status_label = QLabel("✓ 준비")
        self.status_label.setStyleSheet(STATUS_LIGHT if self.theme == 'light' else STATUS_DARK)
        main_layout.addWidget(self.status_label)
        
    def _create_setup_page(self):
        """설정 화면 생성"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        # 파일 선택 섹션
        layout.addWidget(self._create_file_section())
        
        # 설정 섹션
        layout.addWidget(self._create_settings_section())
        
        # 영상 정보 섹션
        layout.addWidget(self._create_info_section())
        
        # 진행 상태
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% 완료")
        layout.addWidget(self.progress_bar)
        
        # 버튼
        btn_layout = QHBoxLayout()
        buttons = BUTTON_LIGHT if self.theme == 'light' else BUTTON_DARK
        
        self.extract_btn = QPushButton("🎬 프레임 미리보기 생성")
        self.extract_btn.setMinimumHeight(50)
        self.extract_btn.setStyleSheet(buttons['extract'])
        self.extract_btn.clicked.connect(self._start_extraction)
        btn_layout.addWidget(self.extract_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return page
        
    def _create_preview_page(self):
        """프레임 선택 화면 생성"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        
        # 상단 정보
        info_layout = QHBoxLayout()
        self.preview_info_label = QLabel("프레임을 선택하고 장면 설명을 입력하세요")
        self.preview_info_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        info_layout.addWidget(self.preview_info_label)
        info_layout.addStretch()
        
        # 전체 선택/해제 버튼
        self.select_all_btn = QPushButton("✓ 전체 선택")
        self.select_all_btn.clicked.connect(self._select_all_frames)
        self.deselect_all_btn = QPushButton("✗ 전체 해제")
        self.deselect_all_btn.clicked.connect(self._deselect_all_frames)
        
        info_layout.addWidget(self.select_all_btn)
        info_layout.addWidget(self.deselect_all_btn)
        
        layout.addLayout(info_layout)
        
        # 프레임 미리보기 그리드
        self.frame_preview_widget = FramePreviewWidget()
        layout.addWidget(self.frame_preview_widget, stretch=1)
        
        # 하단 버튼
        bottom_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("← 뒤로")
        self.back_btn.setMinimumHeight(50)
        self.back_btn.clicked.connect(self._go_back_to_setup)
        bottom_layout.addWidget(self.back_btn)
        
        self.save_progress_bar = QProgressBar()
        self.save_progress_bar.setMinimum(0)
        self.save_progress_bar.setMaximum(100)
        self.save_progress_bar.setValue(0)
        self.save_progress_bar.setVisible(False)
        bottom_layout.addWidget(self.save_progress_bar)
        
        self.save_selected_btn = QPushButton("💾 선택한 프레임 저장")
        self.save_selected_btn.setMinimumHeight(50)
        buttons = BUTTON_LIGHT if self.theme == 'light' else BUTTON_DARK
        self.save_selected_btn.setStyleSheet(buttons['extract'])
        self.save_selected_btn.clicked.connect(self._save_selected_frames)
        bottom_layout.addWidget(self.save_selected_btn)
        
        self.open_folder_btn = QPushButton("📂 결과 폴더 열기")
        self.open_folder_btn.setMinimumHeight(50)
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        bottom_layout.addWidget(self.open_folder_btn)
        
        layout.addLayout(bottom_layout)
        
        return page
        
    def _create_separator(self):
        """구분선 생성"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line
        
    def _create_file_section(self):
        """파일 선택 섹션"""
        group = QGroupBox("📁 파일 선택")
        layout = QVBoxLayout()
        
        # 영상 파일
        video_layout = QHBoxLayout()
        video_label = QLabel("영상 파일:")
        video_label.setMinimumWidth(80)
        self.video_path_edit = QLineEdit()
        self.video_path_edit.setReadOnly(True)
        self.video_path_edit.setPlaceholderText("영상 파일을 선택하세요...")
        video_btn = QPushButton("파일 선택")
        video_btn.clicked.connect(self._select_video_file)
        video_btn.setMinimumWidth(100)
        
        video_layout.addWidget(video_label)
        video_layout.addWidget(self.video_path_edit)
        video_layout.addWidget(video_btn)
        layout.addLayout(video_layout)
        
        # 출력 폴더
        output_layout = QHBoxLayout()
        output_label = QLabel("출력 폴더:")
        output_label.setMinimumWidth(80)
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setReadOnly(True)
        self.output_path_edit.setPlaceholderText("~/Documents/frames_selected (기본값)")
        output_btn = QPushButton("폴더 선택")
        output_btn.clicked.connect(self._select_output_folder)
        output_btn.setMinimumWidth(100)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        group.setLayout(layout)
        return group
        
    def _create_settings_section(self):
        """설정 섹션"""
        group = QGroupBox("⚙️ 추출 설정")
        layout = QVBoxLayout()
        
        # 시간 간격
        interval_layout = QHBoxLayout()
        interval_label = QLabel("시간 간격 (초):")
        interval_label.setMinimumWidth(120)
        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setRange(0.1, 10.0)
        self.interval_spinbox.setSingleStep(0.1)
        self.interval_spinbox.setValue(1.0)
        self.interval_spinbox.setDecimals(1)
        self.interval_spinbox.setSuffix(" 초")
        interval_info = QLabel("(예: 1.0 = 1초마다 프레임 추출)")
        interval_info.setStyleSheet(INFO_TEXT_LIGHT if self.theme == 'light' else INFO_TEXT_DARK)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addWidget(interval_info)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)
        
        # 출력 포맷 안내
        format_info_layout = QHBoxLayout()
        format_info_label = QLabel("📄 출력 포맷: PDF (모든 선택된 프레임을 하나의 PDF로 통합)")
        format_info_label.setStyleSheet(INFO_TEXT_LIGHT if self.theme == 'light' else INFO_TEXT_DARK)
        format_info_layout.addWidget(format_info_label)
        format_info_layout.addStretch()
        layout.addLayout(format_info_layout)
        
        group.setLayout(layout)
        return group
        
    def _create_info_section(self):
        """영상 정보 섹션"""
        group = QGroupBox("ℹ️ 영상 정보")
        layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(120)
        self.info_text.setText("영상을 선택하면 정보가 표시됩니다.")
        
        layout.addWidget(self.info_text)
        group.setLayout(layout)
        return group
        
    def _apply_styles(self):
        """스타일 적용"""
        theme_style = LIGHT_THEME if self.theme == 'light' else DARK_THEME
        self.setStyleSheet(theme_style)
        
    def _select_video_file(self):
        """영상 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "영상 파일 선택",
            "",
            "영상 파일 (*.mp4 *.avi *.mov *.mkv *.flv *.wmv);;모든 파일 (*.*)"
        )
        
        if file_path:
            self.video_path = Path(file_path)
            self.video_path_edit.setText(str(self.video_path))
            self._load_video_info()
            self._update_status(f"영상 선택됨: {self.video_path.name}")
            
    def _select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "출력 폴더 선택"
        )
        
        if folder_path:
            self.output_dir = Path(folder_path)
            self.output_path_edit.setText(str(self.output_dir))
            self._update_status(f"출력 폴더: {self.output_dir}")
            
    def _load_video_info(self):
        """영상 정보 로드"""
        if not self.video_path:
            return
            
        try:
            use_case = GetVideoInfoUseCase(self.repository)
            info = use_case.execute(self.video_path)
            
            interval = self.interval_spinbox.value()
            expected_frames = int(info.duration / interval)
            
            info_text = f"""
<b>파일명:</b> {info.path.name}<br>
<b>길이:</b> {info.duration:.2f}초 ({info.duration / 60:.1f}분)<br>
<b>FPS:</b> {info.fps:.2f}<br>
<b>해상도:</b> {info.width} x {info.height}<br>
<b>총 프레임 수:</b> {info.total_frames:,}<br>
<b>예상 추출 프레임:</b> 약 {expected_frames}개
            """.strip()
            
            self.info_text.setHtml(info_text)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "영상 파일 오류",
                f"영상 정보를 읽을 수 없습니다.\n\n{str(e)}"
            )
            
    def _update_status(self, message: str):
        """상태 메시지 업데이트"""
        self.status_label.setText(message)
        
    def _start_extraction(self):
        """프레임 미리보기 생성"""
        if not self.video_path:
            QMessageBox.warning(self, "경고", "영상 파일을 선택해주세요.")
            return
            
        # 임시 출력 폴더 설정 (사용자 홈 디렉토리 사용)
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "video_frame_extractor_temp"
        self.temp_output_dir = temp_dir
        
        try:
            config = ExtractionConfig(
                interval=self.interval_spinbox.value(),
                output_dir=self.temp_output_dir,
                image_format="pdf",  # PDF로 고정
                image_quality=95
            )
            
            # UI 비활성화
            self.extract_btn.setEnabled(False)
            self._update_status("프레임 추출 중...")
            self.progress_bar.setValue(0)
            
            # 스레드 생성 및 시작
            self.extraction_thread = ExtractionThread(self.video_path, config)
            self.extraction_thread.progress_updated.connect(self._on_progress_updated)
            self.extraction_thread.extraction_completed.connect(self._on_extraction_completed)
            self.extraction_thread.extraction_failed.connect(self._on_extraction_failed)
            self.extraction_thread.start()
            
        except ValueError as e:
            QMessageBox.critical(self, "오류", f"설정 오류: {e}")
            self.extract_btn.setEnabled(True)
            
    @Slot(int)
    def _on_progress_updated(self, value: int):
        """진행 상황 업데이트"""
        self.progress_bar.setValue(value)
        
    @Slot(list)
    def _on_extraction_completed(self, frames: List[VideoFrame]):
        """추출 완료 - 프레임 선택 화면으로 전환"""
        self.progress_bar.setValue(100)
        self.extracted_frames = frames
        
        # 미리보기 위젯에 프레임 설정
        self.frame_preview_widget.set_frames(frames)
        
        # 프레임 선택 화면으로 전환
        self.stack.setCurrentIndex(1)
        
        self._update_status(f"프레임 추출 완료: {len(frames)}개")
        self.extract_btn.setEnabled(True)
        
        # 정보 업데이트
        self.preview_info_label.setText(f"총 {len(frames)}개 프레임 | 선택하고 장면 설명을 입력하세요")
        
    @Slot(str)
    def _on_extraction_failed(self, error_message: str):
        """추출 실패"""
        QMessageBox.critical(
            self,
            "오류",
            f"프레임 추출 중 오류 발생:\n{error_message}"
        )
        
        self._update_status("오류 발생")
        self.extract_btn.setEnabled(True)
        
    def _select_all_frames(self):
        """전체 프레임 선택"""
        self.frame_preview_widget.select_all()
        
    def _deselect_all_frames(self):
        """전체 프레임 선택 해제"""
        self.frame_preview_widget.deselect_all()
        
    def _go_back_to_setup(self):
        """설정 화면으로 돌아가기"""
        self.stack.setCurrentIndex(0)
        
    def _save_selected_frames(self):
        """선택한 프레임 저장"""
        print(f"[DEBUG] _save_selected_frames 호출됨")
        print(f"[DEBUG] 전체 프레임 수: {len(self.extracted_frames)}")
        
        # 직접 extracted_frames에서 선택된 것 확인
        selected_from_extracted = [f for f in self.extracted_frames if f.selected]
        print(f"[DEBUG] extracted_frames에서 선택된 수: {len(selected_from_extracted)}")
        
        selected = self.frame_preview_widget.get_selected_frames()
        print(f"[DEBUG] get_selected_frames에서 반환된 수: {len(selected)}")
        
        if not selected:
            QMessageBox.warning(self, "경고", "선택된 프레임이 없습니다.")
            return
            
        # 출력 폴더 기본값 설정 (사용자 홈 디렉토리 사용)
        if not self.output_dir:
            from pathlib import Path
            home = Path.home()
            self.output_dir = home / "Documents" / "frames_selected"
            
        # 출력 폴더 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # UI 업데이트
        self.save_selected_btn.setEnabled(False)
        self.save_progress_bar.setValue(0)
        self.save_progress_bar.setVisible(True)
        self._update_status(f"선택한 {len(selected)}개 프레임 저장 중...")
        
        # 저장 스레드 시작 (PDF로 고정)
        self.save_thread = SaveSelectedFramesThread(
            self.extracted_frames,
            self.output_dir,
            "pdf"  # PDF로 고정
        )
        self.save_thread.progress_updated.connect(self._on_save_progress_updated)
        self.save_thread.save_completed.connect(self._on_save_completed)
        self.save_thread.save_failed.connect(self._on_save_failed)
        self.save_thread.start()
        
    @Slot(int)
    def _on_save_progress_updated(self, value: int):
        """저장 진행률 업데이트"""
        self.save_progress_bar.setValue(value)
        
    @Slot(int)
    def _on_save_completed(self, saved_count: int):
        """저장 완료"""
        self.save_progress_bar.setValue(100)
        self.save_progress_bar.setVisible(False)
        
        QMessageBox.information(
            self,
            "완료",
            f"✅ 완료!\n\n{saved_count}개의 프레임이 저장되었습니다.\n\n저장 위치: {self.output_dir}"
        )
        
        self._update_status(f"완료: {saved_count}개 프레임 저장")
        self.save_selected_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(True)
        
    @Slot(str)
    def _on_save_failed(self, error_message: str):
        """저장 실패"""
        self.save_progress_bar.setVisible(False)
        
        QMessageBox.critical(
            self,
            "오류",
            f"프레임 저장 중 오류 발생:\n{error_message}"
        )
        
        self._update_status("저장 실패")
        self.save_selected_btn.setEnabled(True)
        
    def _open_output_folder(self):
        """결과 폴더 열기"""
        if self.output_dir and self.output_dir.exists():
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', str(self.output_dir)])
            elif sys.platform == 'win32':  # Windows
                subprocess.run(['explorer', str(self.output_dir)])
            else:  # Linux
                subprocess.run(['xdg-open', str(self.output_dir)])


def main():
    """GUI 메인 진입점"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    theme = 'dark'
    if '--light' in sys.argv:
        theme = 'light'
    elif '--dark' in sys.argv:
        theme = 'dark'
    
    window = VideoFrameExtractorQt(theme=theme)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
