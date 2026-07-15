import sys

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
        QMessageBox, QStackedWidget, QListWidget, QListWidgetItem, QFrame,
        QComboBox, QSpinBox, QDoubleSpinBox, QFormLayout, QGroupBox, QTabWidget,
        QGridLayout
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
    from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
    HAS_PYQT = True

    # Metaclass proxy to map legacy PyQt5-style Qt names to PyQt6-scoped enums
    class QtMeta(type):
        def __getattr__(cls, name):
            if name == 'AlignCenter':
                return Qt.AlignmentFlag.AlignCenter
            elif name == 'AlignLeft':
                return Qt.AlignmentFlag.AlignLeft
            elif name == 'AlignRight':
                return Qt.AlignmentFlag.AlignRight
            elif name == 'AlignVCenter':
                return Qt.AlignmentFlag.AlignVCenter
            elif name == 'Password':
                return QLineEdit.EchoMode.Password
            elif name == 'Horizontal':
                return Qt.Orientation.Horizontal
            elif name == 'Vertical':
                return Qt.Orientation.Vertical
            elif name == 'KeepAspectRatio':
                return Qt.AspectRatioMode.KeepAspectRatio
            elif name == 'SmoothTransformation':
                return Qt.TransformationMode.SmoothTransformation
            return getattr(Qt, name)

    class QtPatch(metaclass=QtMeta):
        pass

    Qt = QtPatch
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
        
    class QFont:
        def __init__(self, *args, **kwargs): pass
        def setBold(self, *args): pass
        
    class QIcon:
        def __init__(self, *args): pass
        
    class QColor:
        def __init__(self, *args): pass
        
    class QPalette:
        pass
        
    def pyqtSignal(*args, **kwargs):
        class DummySignal:
            def connect(self, *args, **kwargs): pass
            def emit(self, *args, **kwargs): pass
        return DummySignal()
