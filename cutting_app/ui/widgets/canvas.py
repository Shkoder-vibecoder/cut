from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItemGroup
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPen, QBrush, QPainter, QFont


class PieceItem(QGraphicsRectItem):
    def __init__(self, x: float, y: float, width: float, height: float, piece_id: int, name: str, color: QColor):
        super().__init__(x, y, width, height)
        self.piece_id = piece_id
        self.piece_name = name
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)

        self.label = QGraphicsTextItem(name[:10], self)
        self.label.setDefaultTextColor(QColor(255, 255, 255))
        self.label.setFont(QFont("Arial", max(6, min(width / 8, 12))))
        self.label.setPos(x + 2, y + height / 2 - 6)


class CuttingCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._zoom_level = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0

    def clear_canvas(self):
        self.scene.clear()
        self._zoom_level = 1.0

    def set_sheet_size(self, width: float, height: float):
        self.scene.clear()
        self.scene.setSceneRect(0, 0, width, height)
        bg = QGraphicsRectItem(0, 0, width, height)
        bg.setBrush(QBrush(QColor(245, 245, 245)))
        bg.setPen(QPen(QColor(180, 180, 180), 2))
        bg.setData(0, "background")
        self.scene.addItem(bg)

        for i in range(1, int(width / 100) + 1):
            line = QGraphicsRectItem(i * 100 - 0.5, 0, 1, height)
            line.setBrush(QBrush(QColor(230, 230, 230)))
            self.scene.addItem(line)

        for i in range(1, int(height / 100) + 1):
            line = QGraphicsRectItem(0, i * 100 - 0.5, width, 1)
            line.setBrush(QBrush(QColor(230, 230, 230)))
            self.scene.addItem(line)

        self.zoom_fit()

    def add_piece(self, x: float, y: float, width: float, height: float, piece_id: int, name: str, color: QColor = None):
        if color is None:
            colors = [QColor(200, 80, 80), QColor(80, 80, 200), QColor(80, 160, 80),
                      QColor(200, 160, 80), QColor(160, 80, 200), QColor(80, 180, 180)]
            color = colors[piece_id % len(colors)]

        item = PieceItem(x, y, width, height, piece_id, name, color)
        item.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable)
        item.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)
        self.scene.addItem(item)
        return item

    def zoom_in(self):
        self.scale(1.2, 1.2)
        self._zoom_level *= 1.2

    def zoom_out(self):
        self.scale(0.8, 0.8)
        self._zoom_level *= 0.8

    def zoom_fit(self):
        if self.scene.sceneRect().isEmpty():
            return
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_level = 1.0

    def zoom_reset(self):
        self.resetTransform()
        self._zoom_level = 1.0

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0 and self._zoom_level < self._max_zoom:
                self.scale(1.1, 1.1)
                self._zoom_level *= 1.1
            elif delta < 0 and self._zoom_level > self._min_zoom:
                self.scale(0.9, 0.9)
                self._zoom_level *= 0.9
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, PieceItem):
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
            else:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mouseReleaseEvent(event)