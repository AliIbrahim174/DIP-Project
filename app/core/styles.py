"""
styles.py
=========
All Qt stylesheets and shared colour constants for MedVision Workbench.
Import DARK_STYLE and SIDEBAR_STYLE wherever needed.
"""

# ── Colour tokens ─────────────────────────────────────────────────────────────
BG_DEEP    = "#0a0c10"
BG_PANEL   = "#0f1117"
BG_CARD    = "#141824"
BORDER     = "#1e2230"
BORDER_MID = "#1a2030"
ACCENT     = "#00c8ff"
ACCENT2    = "#0057ff"
TEXT_DIM   = "#7080a0"
TEXT_MID   = "#a0b4cc"
TEXT_MAIN  = "#c0cce0"
WARN       = "#f0a050"

# ── Application-wide dark theme ───────────────────────────────────────────────
DARK_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_MAIN};
}}
QMenuBar {{
    background: #0d1018;
    color: #8899b0;
    border-bottom: 1px solid {BORDER_MID};
}}
QMenuBar::item:selected {{ background: #1a2540; color: {ACCENT}; }}
QMenu {{
    background: #0f1420;
    color: {TEXT_MID};
    border: 1px solid #1e2a3a;
}}
QMenu::item:selected {{ background: #1a2540; color: {ACCENT}; }}
QToolBar {{
    background: #0d1018;
    border-bottom: 1px solid {BORDER_MID};
    spacing: 4px;
    padding: 2px 4px;
}}
QStatusBar {{
    background: #080a0e;
    color: #4a6080;
    font-size: 10px;
    border-top: 1px solid {BORDER_MID};
}}
QSplitter::handle {{ background: {BORDER_MID}; width: 1px; height: 1px; }}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    background: {BG_DEEP};
}}
QTabBar::tab {{
    background: #0d1018;
    color: #607080;
    padding: 6px 16px;
    border: 1px solid {BORDER_MID};
    border-bottom: none;
    font-size: 10px;
}}
QTabBar::tab:selected {{
    background: {BG_DEEP};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
QProgressBar {{
    background: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 3px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{ background: {ACCENT2}; border-radius: 3px; }}
QScrollBar:vertical {{
    background: #0d1018; width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #2a3550; border-radius: 4px; min-height: 20px;
}}
QScrollBar:horizontal {{
    background: #0d1018; height: 8px; border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: #2a3550; border-radius: 4px; min-width: 20px;
}}
"""

# ── Tools sidebar shared style ────────────────────────────────────────────────
SIDEBAR_STYLE = f"""
    QGroupBox {{
        color: {TEXT_DIM};
        font-size: 10px;
        font-weight: bold;
        border: 1px solid {BORDER};
        border-radius: 5px;
        margin-top: 8px;
        padding-top: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 8px;
        color: #4080c0;
    }}
    QPushButton {{
        background: {BG_CARD};
        color: {TEXT_MID};
        border: 1px solid #1e2a3a;
        border-radius: 4px;
        padding: 5px 8px;
        font-size: 10px;
        text-align: left;
    }}
    QPushButton:hover {{ background: #1a2540; color: {ACCENT}; border-color: #204060; }}
    QPushButton:pressed {{ background: #0d1628; }}
    QLabel {{ color: {TEXT_DIM}; font-size: 10px; }}
    QSpinBox, QDoubleSpinBox, QComboBox {{
        background: {BG_PANEL};
        color: {TEXT_MID};
        border: 1px solid {BORDER};
        border-radius: 3px;
        padding: 2px 4px;
        font-size: 10px;
    }}
    QComboBox::drop-down {{ border: none; }}
    QComboBox QAbstractItemView {{
        background: {BG_CARD};
        color: {TEXT_MID};
        selection-background-color: #1a2540;
    }}
"""

# ── Toolbar button style (reusable) ──────────────────────────────────────────
TOOLBAR_BTN_STYLE = f"""
    QPushButton {{
        background: {BG_CARD}; color: #80a0c0;
        border: 1px solid #1e2a3a; border-radius: 4px;
        padding: 0 10px; font-size: 11px;
    }}
    QPushButton:hover {{ background: #1a2540; color: {ACCENT}; }}
"""

# ── Pipeline panel list style ─────────────────────────────────────────────────
PIPELINE_LIST_STYLE = f"""
    QListWidget {{
        background: {BG_PANEL};
        border: 1px solid {BORDER};
        border-radius: 4px;
        color: #c8d0e0;
        font-size: 10px;
    }}
    QListWidget::item {{ padding: 4px 6px; border-bottom: 1px solid #1a1e2a; }}
    QListWidget::item:selected {{ background: #1a2540; color: {ACCENT}; }}
"""

PIPELINE_UNDO_STYLE = f"""
    QPushButton {{
        background: #1a1e2a; color: {WARN};
        border: 1px solid #2a3040; border-radius: 4px;
        padding: 5px; font-size: 10px;
    }}
    QPushButton:hover {{ background: #252c40; }}
"""

# ── Metadata text area ────────────────────────────────────────────────────────
METADATA_TEXT_STYLE = f"""
    QTextEdit {{
        background: {BG_PANEL};
        border: 1px solid {BORDER};
        border-radius: 4px;
        color: #8899b0;
        font-size: 10px;
        font-family: 'Courier New', monospace;
    }}
"""