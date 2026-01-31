"""
GUI 테마 정의
"""

LIGHT_THEME = """
    /* 메인 윈도우 */
    QMainWindow {
        background-color: #f5f7fa;
    }
    
    /* 그룹박스 */
    QGroupBox {
        font-size: 14px;
        font-weight: bold;
        color: #2c3e50;
        background-color: #ffffff;
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        margin-top: 15px;
        padding-top: 15px;
        padding: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 15px;
        padding: 0 8px;
        background-color: #ffffff;
    }
    
    /* 입력 필드 */
    QLineEdit {
        padding: 10px;
        border: 1px solid #d1d9e6;
        border-radius: 5px;
        font-size: 13px;
        background-color: #ffffff;
        color: #2c3e50;
    }
    QLineEdit:focus {
        border: 2px solid #3498db;
    }
    QLineEdit:read-only {
        background-color: #f5f7fa;
        color: #7f8c8d;
    }
    
    /* 버튼 */
    QPushButton {
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 500;
        border-radius: 5px;
        border: none;
        background-color: #3498db;
        color: white;
    }
    QPushButton:hover {
        background-color: #2980b9;
    }
    QPushButton:pressed {
        background-color: #21618c;
    }
    QPushButton:disabled {
        background-color: #bdc3c7;
        color: #95a5a6;
    }
    
    /* 콤보박스, 스핀박스 */
    QComboBox, QSpinBox, QDoubleSpinBox {
        padding: 8px;
        border: 1px solid #d1d9e6;
        border-radius: 5px;
        min-width: 100px;
        background-color: #ffffff;
        color: #2c3e50;
    }
    QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #3498db;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 5px;
    }
    
    /* 슬라이더 */
    QSlider::groove:horizontal {
        height: 8px;
        background: #ecf0f1;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #3498db;
        width: 18px;
        height: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    QSlider::handle:horizontal:hover {
        background: #2980b9;
    }
    
    /* 텍스트 에디터 */
    QTextEdit {
        border: 1px solid #d1d9e6;
        border-radius: 5px;
        background-color: #ffffff;
        color: #2c3e50;
        padding: 10px;
    }
    
    /* 프로그레스 바 */
    QProgressBar {
        border: 1px solid #d1d9e6;
        border-radius: 5px;
        text-align: center;
        height: 35px;
        background-color: #ffffff;
        color: #2c3e50;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #3498db, stop:1 #2ecc71);
        border-radius: 4px;
    }
    
    /* 라벨 */
    QLabel {
        color: #2c3e50;
    }
"""

DARK_THEME = """
    /* 메인 윈도우 */
    QMainWindow {
        background-color: #1e1e1e;
    }
    
    /* 그룹박스 */
    QGroupBox {
        font-size: 14px;
        font-weight: bold;
        color: #e0e0e0;
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        margin-top: 15px;
        padding-top: 15px;
        padding: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 15px;
        padding: 0 8px;
        background-color: #2d2d2d;
    }
    
    /* 입력 필드 */
    QLineEdit {
        padding: 10px;
        border: 1px solid #3d3d3d;
        border-radius: 5px;
        font-size: 13px;
        background-color: #252525;
        color: #e0e0e0;
    }
    QLineEdit:focus {
        border: 2px solid #5dade2;
    }
    QLineEdit:read-only {
        background-color: #1e1e1e;
        color: #808080;
    }
    
    /* 버튼 */
    QPushButton {
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 500;
        border-radius: 5px;
        border: none;
        background-color: #5dade2;
        color: white;
    }
    QPushButton:hover {
        background-color: #3498db;
    }
    QPushButton:pressed {
        background-color: #2980b9;
    }
    QPushButton:disabled {
        background-color: #404040;
        color: #707070;
    }
    
    /* 콤보박스, 스핀박스 */
    QComboBox, QSpinBox, QDoubleSpinBox {
        padding: 8px;
        border: 1px solid #3d3d3d;
        border-radius: 5px;
        min-width: 100px;
        background-color: #252525;
        color: #e0e0e0;
    }
    QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #5dade2;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 5px;
    }
    QComboBox QAbstractItemView {
        background-color: #252525;
        color: #e0e0e0;
        selection-background-color: #5dade2;
    }
    
    /* 슬라이더 */
    QSlider::groove:horizontal {
        height: 8px;
        background: #404040;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #5dade2;
        width: 18px;
        height: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    QSlider::handle:horizontal:hover {
        background: #3498db;
    }
    
    /* 텍스트 에디터 */
    QTextEdit {
        border: 1px solid #3d3d3d;
        border-radius: 5px;
        background-color: #252525;
        color: #e0e0e0;
        padding: 10px;
    }
    
    /* 프로그레스 바 */
    QProgressBar {
        border: 1px solid #3d3d3d;
        border-radius: 5px;
        text-align: center;
        height: 35px;
        background-color: #252525;
        color: #e0e0e0;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #5dade2, stop:1 #58d68d);
        border-radius: 4px;
    }
    
    /* 라벨 */
    QLabel {
        color: #e0e0e0;
    }
    
    /* 구분선 */
    QFrame[frameShape="4"] {
        color: #3d3d3d;
    }
"""

BUTTON_LIGHT = {
    'extract': """
        QPushButton {
            background-color: #27ae60;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            border: none;
        }
        QPushButton:hover {
            background-color: #229954;
        }
        QPushButton:pressed {
            background-color: #1e8449;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #95a5a6;
        }
    """,
    'open_folder': """
        QPushButton {
            background-color: #3498db;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            border: none;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #95a5a6;
        }
    """
}

BUTTON_DARK = {
    'extract': """
        QPushButton {
            background-color: #58d68d;
            color: #1e1e1e;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            border: none;
        }
        QPushButton:hover {
            background-color: #52be80;
        }
        QPushButton:pressed {
            background-color: #45b570;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #707070;
        }
    """,
    'open_folder': """
        QPushButton {
            background-color: #5dade2;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            border: none;
        }
        QPushButton:hover {
            background-color: #3498db;
        }
        QPushButton:pressed {
            background-color: #2980b9;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #707070;
        }
    """
}

STATUS_LIGHT = """
    QLabel { 
        padding: 12px; 
        background-color: #ffffff; 
        border: 1px solid #d1d9e6;
        border-radius: 5px;
        color: #2c3e50;
        font-weight: 500;
    }
"""

STATUS_DARK = """
    QLabel { 
        padding: 12px; 
        background-color: #252525; 
        border: 1px solid #3d3d3d;
        border-radius: 5px;
        color: #e0e0e0;
        font-weight: 500;
    }
"""

INFO_TEXT_LIGHT = "color: #7f8c8d; font-size: 12px;"
INFO_TEXT_DARK = "color: #a0a0a0; font-size: 12px;"

TITLE_LIGHT = "color: #2c3e50; padding: 10px;"
TITLE_DARK = "color: #e0e0e0; padding: 10px;"
