from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPixmap


class TitleBarButton(QPushButton):
    def __init__(self, symbol=None, bg_color=None, hover_color=None, image_path=None, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.bg_color = bg_color or "#666666"
        self.hover_color = hover_color or "#888888"
        self.setFixedSize(30, 30)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none; border-radius: 6px;")
        self.hover = False
        self.pixmap = QPixmap(image_path) if image_path else None

    def enterEvent(self, event):
        self.hover = True
        self.update()

    def leaveEvent(self, event):
        self.hover = False
        self.update()

    def setImage(self, path):
        self.pixmap = QPixmap(path)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # hover background (subtle)
        if self.hover:
            painter.fillRect(self.rect(), QColor(self.hover_color))

        if self.pixmap and not self.pixmap.isNull():
            # scale pixmap preserving aspect ratio, center it
            pm = self.pixmap.scaled(self.width()-6, self.height()-6, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (self.width() - pm.width()) // 2
            y = (self.height() - pm.height()) // 2
            painter.drawPixmap(x, y, pm)
            return

        # if there's no pixmap draw a symbol (text)
        if self.symbol:
            painter.setPen(Qt.white)
            f = painter.font()
            f.setBold(True)
            f.setPointSize(12)
            painter.setFont(f)
            painter.drawText(self.rect(), Qt.AlignCenter, self.symbol)
            return
  
        # fallback: fill a small neutral background
        painter.fillRect(self.rect(), QColor(self.bg_color))


class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)   # True = Gaming Mode, False = Study Mode

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(170, 40)
        self.checked = False      # default = Study Mode
        self._circle_x = 5

    def mousePressEvent(self, event):
        self.checked = not self.checked
        self.animate()
        self.toggled.emit(self.checked)

    def animate(self):
        circle_diameter = 30
        margin = 5
        self._circle_x = self.width() - circle_diameter - margin if self.checked else margin
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background pill
        bg = QColor("#ef4444") if self.checked else QColor("#3b82f6")
        painter.setBrush(bg)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

        # Toggle thumb (circle)
        painter.setBrush(Qt.white)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self._circle_x, 5, 30, 30)

