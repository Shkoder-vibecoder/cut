from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItemGroup
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPen, QBrush, QFont


class PieceItem(QGraphicsItemGroup):
    def __init__(self, piece_id: int, order_item_id: int, name: str, x: float, y: float, width: float, height: float, color: QColor = None):
        super().__init__()

        if color is None:
            colors = [
                QColor(200, 80, 80), QColor(80, 80, 200), QColor(80, 160, 80),
                QColor(200, 160, 80), QColor(160, 80, 200), QColor(80, 180, 180),
                QColor(200, 200, 80), QColor(150, 100, 150)
            ]
            color = colors[piece_id % len(colors)]

        self.piece_id = piece_id
        self.order_item_id = order_item_id
        self.piece_name = name

        self.rect_item = QGraphicsRectItem(x, y, width, height, self)
        self.rect_item.setBrush(QBrush(color))
        self.rect_item.setPen(QPen(Qt.GlobalColor.black, 1))
        self.rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.rect_item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)

        short_name = name[:10] if len(name) > 10 else name
        font_size = max(6, min(width / 8, 12))
        self.label = QGraphicsTextItem(short_name, self)
        self.label.setDefaultTextColor(QColor(255, 255, 255))
        self.label.setFont(QFont("Arial", font_size))
        self.label.setPos(x + 2, y + height / 2 - font_size / 2)

        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable)
        self.setData(0, "piece")
        self.setData(1, piece_id)
        self.setData(2, order_item_id)
        self.setData(3, name)

    def get_info(self) -> dict:
        return {
            "id": self.piece_id,
            "order_item_id": self.order_item_id,
            "name": self.piece_name,
            "x": self.x(),
            "y": self.y(),
            "width": self.rect_item.rect().width(),
            "height": self.rect_item.rect().height()
        }

    def rotate_90(self):
        rect = self.rect_item.rect()
        new_rect = QRectF(rect.y(), rect.x(), rect.height(), rect.width())
        self.rect_item.setRect(new_rect)

        new_x = self.x() + rect.width() - new_rect.width()
        new_y = self.y() + rect.height() - new_rect.height()
        self.setPos(new_x, new_y)

    def update_label(self):
        x = self.x()
        y = self.y()
        w = self.rect_item.rect().width()
        h = self.rect_item.rect().height()
        font_size = max(6, min(w / 8, 12))
        self.label.setFont(QFont("Arial", font_size))
        self.label.setPos(x + 2, y + h / 2 - font_size / 2)