from pos_app.ui.mock_pyqt import *

class SalesOverTimeChart(QWidget):
    """Custom high-fidelity line/bar chart displaying sales revenue over time."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = [] # list of dict: [{"date": "2026-07-10", "revenue": 150.0}, ...]
        self.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 6px;")
        
    def setData(self, data):
        self.data = data
        self.update() # trigger paintEvent

    def paintEvent(self, event):
        if not HAS_PYQT:
            return
            
        painter = QPainter(self)
        try:
            # Set antialiasing
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            except AttributeError:
                pass
                
            rect = self.rect()
            
            # Margins
            margin_left = 60
            margin_right = 20
            margin_top = 40
            margin_bottom = 40
            
            w = rect.width() - margin_left - margin_right
            h = rect.height() - margin_top - margin_bottom
            
            if w <= 0 or h <= 0:
                return
                
            # Background
            painter.fillRect(rect, QColor("#ffffff"))
            
            # Title
            painter.setPen(QColor("#0f172a"))
            font_title = QFont("Segoe UI", 11)
            font_title.setBold(True)
            painter.setFont(font_title)
            painter.drawText(20, 25, "Daily Revenue Trend")
            
            if not self.data:
                painter.setPen(QColor("#94a3b8"))
                painter.setFont(QFont("Segoe UI", 10))
                painter.drawText(rect.width() // 2 - 50, rect.height() // 2, "No sales data available")
                return
                
            # Find scale limits
            max_val = max(item["revenue"] for item in self.data)
            if max_val == 0:
                max_val = 1.0
            max_val *= 1.15 # pad top by 15%
            
            num_points = len(self.data)
            col_width = w / max(1, num_points)
            
            # Draw axes lines
            pen_grid = QPen(QColor("#f1f5f9"), 1)
            painter.setPen(pen_grid)
            
            # Draw Y gridlines and labels (4 levels)
            for i in range(5):
                y_pos = int(margin_top + h - (i * h / 4))
                val = i * max_val / 4
                painter.setPen(pen_grid)
                painter.drawLine(margin_left, y_pos, margin_left + w, y_pos)
                
                # Label
                painter.setPen(QColor("#64748b"))
                painter.setFont(QFont("Segoe UI", 8))
                painter.drawText(10, y_pos + 4, f"${val:.0f}")
                
            # Draw points / bars
            prev_x = None
            prev_y = None
            
            for index, item in enumerate(self.data):
                # Calculate coordinates
                x = int(margin_left + (index * col_width) + (col_width / 2))
                y = int(margin_top + h - (item["revenue"] * h / max_val))
                
                # Draw Bar/Column
                painter.setBrush(QColor("#3b82f6"))
                painter.setPen(QPen(QColor("#2563eb"), 1))
                bar_width = max(6, int(col_width * 0.4))
                painter.drawRect(x - bar_width // 2, y, bar_width, int(margin_top + h - y))
                
                # Draw Trend Line
                if prev_x is not None:
                    pen_line = QPen(QColor("#ef4444"), 2)
                    painter.setPen(pen_line)
                    painter.drawLine(prev_x, prev_y, x, y)
                    
                prev_x = x
                prev_y = y
                
                # Draw date label
                painter.setPen(QColor("#64748b"))
                painter.setFont(QFont("Segoe UI", 8))
                date_label = item["date"][-5:] # MM-DD format
                painter.drawText(x - 15, margin_top + h + 20, date_label)
                
        finally:
            painter.end()


class CategoryBreakdownChart(QWidget):
    """Custom high-fidelity bar chart displaying total revenue compiled by product category."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = [] # list of dict: [{"category": "Produce", "revenue": 1200.0}, ...]
        self.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 6px;")
        
    def setData(self, data):
        self.data = data
        self.update() # trigger paintEvent

    def paintEvent(self, event):
        if not HAS_PYQT:
            return
            
        painter = QPainter(self)
        try:
            # Set antialiasing
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            except AttributeError:
                pass
                
            rect = self.rect()
            
            # Margins
            margin_left = 80
            margin_right = 40
            margin_top = 40
            margin_bottom = 20
            
            w = rect.width() - margin_left - margin_right
            h = rect.height() - margin_top - margin_bottom
            
            if w <= 0 or h <= 0:
                return
                
            # Background
            painter.fillRect(rect, QColor("#ffffff"))
            
            # Title
            painter.setPen(QColor("#0f172a"))
            font_title = QFont("Segoe UI", 11)
            font_title.setBold(True)
            painter.setFont(font_title)
            painter.drawText(20, 25, "Sales by Category")
            
            if not self.data:
                painter.setPen(QColor("#94a3b8"))
                painter.setFont(QFont("Segoe UI", 10))
                painter.drawText(rect.width() // 2 - 50, rect.height() // 2, "No categorical sales")
                return
                
            # Horizontal bar layout
            num_cats = len(self.data)
            row_height = h / max(1, num_cats)
            
            max_val = max(item["revenue"] for item in self.data)
            if max_val == 0:
                max_val = 1.0
                
            # Color palette
            colors = [
                QColor("#10b981"), # Green
                QColor("#6366f1"), # Indigo
                QColor("#f59e0b"), # Amber
                QColor("#ec4899"), # Pink
                QColor("#8b5cf6"), # Purple
                QColor("#3b82f6")  # Blue
            ]
            
            for index, item in enumerate(self.data):
                y = int(margin_top + (index * row_height) + (row_height * 0.2))
                bar_h = int(row_height * 0.6)
                
                bar_w = int((item["revenue"] / max_val) * w)
                
                # Draw bar
                color = colors[index % len(colors)]
                painter.setBrush(color)
                painter.setPen(Qt.PenStyle.NoPen if hasattr(Qt, "PenStyle") else 0)
                painter.drawRect(margin_left, y, bar_w, bar_h)
                
                # Category label (on left)
                painter.setPen(QColor("#334155"))
                painter.setFont(QFont("Segoe UI", 9))
                label_text = item["category"][:10]
                painter.drawText(10, y + (bar_h // 2) + 4, label_text)
                
                # Value label (on right of bar)
                painter.setPen(QColor("#475569"))
                painter.drawText(margin_left + bar_w + 5, y + (bar_h // 2) + 4, f"${item['revenue']:.2f}")
                
        finally:
            painter.end()
