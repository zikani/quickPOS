import sys

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView as _RealQHeaderView,
        QMessageBox, QStackedWidget, QListWidget, QListWidgetItem, QFrame,
        QComboBox, QSpinBox, QDoubleSpinBox, QFormLayout, QGroupBox, QTabWidget,
        QGridLayout
    )
    from PyQt6.QtCore import Qt as _RealQt, pyqtSignal, QSize, QTimer, QThread
    from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QPainter, QPen, QBrush, QImage, QPixmap
    HAS_PYQT = True

    # Metaclass proxy to map legacy PyQt5-style Qt names to PyQt6-scoped enums
    class QtMeta(type):
        def __getattr__(cls, name):
            if name == 'AlignCenter':
                return _RealQt.AlignmentFlag.AlignCenter
            elif name == 'AlignLeft':
                return _RealQt.AlignmentFlag.AlignLeft
            elif name == 'AlignRight':
                return _RealQt.AlignmentFlag.AlignRight
            elif name == 'AlignVCenter':
                return _RealQt.AlignmentFlag.AlignVCenter
            elif name == 'Password':
                return QLineEdit.EchoMode.Password
            elif name == 'Horizontal':
                return _RealQt.Orientation.Horizontal
            elif name == 'Vertical':
                return _RealQt.Orientation.Vertical
            elif name == 'KeepAspectRatio':
                return _RealQt.AspectRatioMode.KeepAspectRatio
            elif name == 'SmoothTransformation':
                return _RealQt.TransformationMode.SmoothTransformation
            return getattr(_RealQt, name)

    class QtPatch(metaclass=QtMeta):
        AlignCenter = _RealQt.AlignmentFlag.AlignCenter
        AlignLeft = _RealQt.AlignmentFlag.AlignLeft
        AlignRight = _RealQt.AlignmentFlag.AlignRight
        AlignVCenter = _RealQt.AlignmentFlag.AlignVCenter
        Password = QLineEdit.EchoMode.Password
        Horizontal = _RealQt.Orientation.Horizontal
        Vertical = _RealQt.Orientation.Vertical
        KeepAspectRatio = _RealQt.AspectRatioMode.KeepAspectRatio
        SmoothTransformation = _RealQt.TransformationMode.SmoothTransformation

    Qt = QtPatch

    # Metaclass proxy to map legacy PyQt5-style QHeaderView names to PyQt6-scoped enums
    class QHeaderViewMeta(type):
        def __getattr__(cls, name):
            if name == 'Stretch':
                return _RealQHeaderView.ResizeMode.Stretch
            elif name == 'Interactive':
                return _RealQHeaderView.ResizeMode.Interactive
            elif name == 'Fixed':
                return _RealQHeaderView.ResizeMode.Fixed
            elif name == 'ResizeToContents':
                return _RealQHeaderView.ResizeMode.ResizeToContents
            return getattr(_RealQHeaderView, name)

    class QHeaderViewPatch(metaclass=QHeaderViewMeta):
        Stretch = _RealQHeaderView.ResizeMode.Stretch
        Interactive = _RealQHeaderView.ResizeMode.Interactive
        Fixed = _RealQHeaderView.ResizeMode.Fixed
        ResizeToContents = _RealQHeaderView.ResizeMode.ResizeToContents

    QHeaderView = QHeaderViewPatch
except ImportError:
    HAS_PYQT = False
    
    class MockSignal:
        def __init__(self): pass
        def connect(self, callback): pass
        def disconnect(self, callback=None): pass
        def emit(self, *args, **kwargs): pass
        
    # Mock classes so that python3 compiles perfectly
    class QApplication:
        def __init__(self, *args): pass
        def exec(self): return 0
        @staticmethod
        def setStyleSheet(*args): pass
    
    class QMainWindow:
        def __init__(self, *args, **kwargs): pass
        def setCentralWidget(self, *args): pass
        def setWindowTitle(self, *args): pass
        def setMinimumSize(self, *args): pass
        def show(self): pass
        def showMaximized(self): pass
        def setStyleSheet(self, *args): pass
        
    class QWidget:
        def __init__(self, parent=None, *args, **kwargs): pass
        def setMinimumSize(self, *args): pass
        def setMaximumSize(self, *args): pass
        def setStyleSheet(self, *args): pass
        def setLayout(self, *args): pass
        def show(self): pass
        def hide(self): pass
        
    class QDialog:
        def __init__(self, parent=None, *args, **kwargs): pass
        def setWindowTitle(self, *args): pass
        def setMinimumSize(self, *args): pass
        def setLayout(self, *args): pass
        def setStyleSheet(self, *args): pass
        def exec(self): return 1
        def accept(self): pass
        def reject(self): pass
        
    class QVBoxLayout:
        def __init__(self, *args, **kwargs): pass
        def addWidget(self, *args, **kwargs): pass
        def addLayout(self, *args, **kwargs): pass
        def addStretch(self, *args, **kwargs): pass
        def setContentsMargins(self, *args, **kwargs): pass
        def setSpacing(self, *args, **kwargs): pass
        
    class QHBoxLayout:
        def __init__(self, *args, **kwargs): pass
        def addWidget(self, *args, **kwargs): pass
        def addLayout(self, *args, **kwargs): pass
        def addStretch(self, *args, **kwargs): pass
        def setContentsMargins(self, *args, **kwargs): pass
        def setSpacing(self, *args, **kwargs): pass
        
    class QGridLayout:
        def __init__(self, *args, **kwargs): pass
        def addWidget(self, *args, **kwargs): pass
        def setContentsMargins(self, *args, **kwargs): pass
        def setSpacing(self, *args, **kwargs): pass
        
    class QPushButton:
        def __init__(self, *args, **kwargs):
            self.clicked = MockSignal()
        def setStyleSheet(self, *args): pass
        def setEnabled(self, *args): pass
        def setMinimumSize(self, *args): pass
        def setFixedSize(self, *args): pass
        
    class QLabel:
        def __init__(self, *args, **kwargs): pass
        def setStyleSheet(self, *args): pass
        def setText(self, *args): pass
        def setAlignment(self, *args): pass
        
    class QLineEdit:
        def __init__(self, *args, **kwargs):
            self.textChanged = MockSignal()
            self.returnPressed = MockSignal()
        def setPlaceholderText(self, *args): pass
        def setEchoMode(self, *args): pass
        def text(self) -> str: return ""
        def setText(self, *args): pass
        def setFocus(self): pass
        def clear(self): pass
        
    class QTableWidget:
        def __init__(self, *args, **kwargs):
            self.cellClicked = MockSignal()
            self.cellDoubleClicked = MockSignal()
            self.itemChanged = MockSignal()
        def setColumnCount(self, *args): pass
        def setRowCount(self, *args): pass
        def setHorizontalHeaderLabels(self, *args): pass
        def horizontalHeader(self): return QHeaderView()
        def setItem(self, *args): pass
        def clearContents(self): pass
        def setRowCount(self, *args): pass
        def removeRow(self, *args): pass
        def verticalHeader(self): return QHeaderView()
        def setSelectionBehavior(self, *args): pass
        def setEditTriggers(self, *args): pass
        def currentColumn(self) -> int: return 0
        def currentRow(self) -> int: return 0
        def item(self, row, column): return QTableWidgetItem()
        
    class QTableWidgetItem:
        def __init__(self, *args, **kwargs): pass
        def setTextAlignment(self, *args): pass
        
    class QHeaderView:
        Stretch = 1
        Interactive = 2
        Fixed = 3
        ResizeToContents = 4
        def setSectionResizeMode(self, *args): pass
        def setStretchLastSection(self, *args): pass
        
    class QMessageBox:
        StandardButton = object()
        Yes = 16384
        No = 65536
        Ok = 1024
        @staticmethod
        def information(*args, **kwargs): pass
        @staticmethod
        def warning(*args, **kwargs): pass
        @staticmethod
        def critical(*args, **kwargs): pass
        @staticmethod
        def question(*args, **kwargs): return 16384
        
    class QStackedWidget:
        def __init__(self, *args, **kwargs): pass
        def addWidget(self, *args): pass
        def setCurrentWidget(self, *args): pass
        def setCurrentIndex(self, *args): pass
        
    class QListWidget:
        def __init__(self, *args, **kwargs): pass
        def addItem(self, *args): pass
        def clear(self): pass
        def currentItem(self): return QListWidgetItem()
        def currentRow(self) -> int: return 0
        
    class QListWidgetItem:
        def __init__(self, *args, **kwargs): pass
        def text(self) -> str: return ""
        
    class QFrame:
        def __init__(self, *args, **kwargs): pass
        def setFrameShape(self, *args): pass
        def setFrameShadow(self, *args): pass
        def setStyleSheet(self, *args): pass
        
    class QComboBox:
        def __init__(self, *args, **kwargs):
            self.currentIndexChanged = MockSignal()
        def addItem(self, *args): pass
        def addItems(self, *args): pass
        def clear(self): pass
        def currentText(self) -> str: return ""
        def currentIndex(self) -> int: return 0
        def setCurrentIndex(self, *args): pass
        
    class QSpinBox:
        def __init__(self, *args, **kwargs):
            self.valueChanged = MockSignal()
        def setRange(self, *args): pass
        def setValue(self, *args): pass
        def value(self) -> int: return 1
        
    class QDoubleSpinBox:
        def __init__(self, *args, **kwargs):
            self.valueChanged = MockSignal()
        def setRange(self, *args): pass
        def setValue(self, *args): pass
        def value(self) -> float: return 0.0
        def setPrefix(self, *args): pass
        
    class QFormLayout:
        def __init__(self, *args, **kwargs): pass
        def addRow(self, *args): pass
        
    class QGroupBox:
        def __init__(self, *args, **kwargs): pass
        def setLayout(self, *args): pass
        
    class QTabWidget:
        def __init__(self, *args, **kwargs): pass
        def addTab(self, *args): pass
        
    class Qt:
        Horizontal = 1
        Vertical = 2
        AlignLeft = 1
        AlignRight = 2
        AlignCenter = 4
        AlignVCenter = 8
        WidgetAttribute = object()
        Password = 2
        KeepAspectRatio = 1
        SmoothTransformation = 2
        
    class QSize:
        def __init__(self, *args): pass
        
    class QTimer:
        def __init__(self, *args, **kwargs): pass
        def start(self, *args): pass
        def stop(self): pass
        @staticmethod
        def singleShot(*args): pass
        
    class QThread:
        def __init__(self, parent=None): pass
        def start(self): pass
        def stop(self): pass
        def wait(self): pass
        def msleep(self, ms: int): pass
        
    class QImage:
        class Format:
            Format_RGB888 = 1
        def __init__(self, *args, **kwargs): pass
        
    class QPixmap:
        def __init__(self, *args, **kwargs): pass
        @staticmethod
        def fromImage(img): return QPixmap()
        def scaled(self, *args, **kwargs): return self
        
    class QFont:
        def __init__(self, *args, **kwargs): pass
        def setBold(self, *args): pass
        
    class QIcon:
        def __init__(self, *args): pass
        
    class QColor:
        def __init__(self, *args): pass
        
    class QPalette:
        pass
        
    class QPainter:
        def __init__(self, *args): pass
        def begin(self, *args): return True
        def end(self): pass
        def setPen(self, *args): pass
        def setBrush(self, *args): pass
        def drawLine(self, *args): pass
        def drawRect(self, *args): pass
        def drawText(self, *args): pass
        def drawEllipse(self, *args): pass
        def setRenderHint(self, *args): pass
        
    class QPen:
        def __init__(self, *args, **kwargs): pass
        
    class QBrush:
        def __init__(self, *args, **kwargs): pass
        
    def pyqtSignal(*args, **kwargs):
        class DummySignal:
            def connect(self, *args, **kwargs): pass
            def emit(self, *args, **kwargs): pass
        return DummySignal()
