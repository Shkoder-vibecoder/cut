from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QLabel, QMessageBox, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen, QBrush, QPainter, QFont
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem
from db.models import TaskSheet, Placement, CuttingTask


class CanvasView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self._zoom = 1.0

    def clear_canvas(self):
        self.scene.clear()

    def draw_sheet(self, width: float, height: float, sheet_index: int):
        self.scene.clear()
        self.scene.setSceneRect(0, 0, width, height)

        bg = QGraphicsRectItem(0, 0, width, height)
        bg.setBrush(QBrush(QColor(240, 240, 240)))
        bg.setPen(QPen(QColor(100, 100, 100)))
        self.scene.addItem(bg)

        text = QGraphicsTextItem(f"Лист {sheet_index + 1}")
        text.setDefaultTextColor(QColor(0, 0, 0))
        text.setPos(10, height - 20)
        self.scene.addItem(text)

        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def add_piece(self, x: float, y: float, w: float, h: float, name: str, color: QColor):
        rect = QGraphicsRectItem(x, y, w, h)
        rect.setBrush(QBrush(color))
        rect.setPen(QPen(QColor(0, 0, 0), 1))
        self.scene.addItem(rect)

        label = QGraphicsTextItem(name[:8])
        label.setDefaultTextColor(QColor(255, 255, 255))
        label.setFont(QFont("Arial", 8))
        label.setPos(x + 2, y + h / 2 - 6)
        self.scene.addItem(label)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.scale(1.1, 1.1)
                self._zoom *= 1.1
            else:
                self.scale(0.9, 0.9)
                self._zoom *= 0.9
        else:
            super().wheelEvent(event)


class ResultView(QWidget):
    def __init__(self, job_service, export_service, session):
        super().__init__()
        self.job_service = job_service
        self.export_service = export_service
        self.session = session
        self._current_task = None
        self._current_sheet_index = 0
        self._colors = [
            QColor(255, 100, 100), QColor(100, 100, 255), QColor(100, 200, 100),
            QColor(255, 150, 50), QColor(200, 100, 200), QColor(100, 200, 200),
            QColor(255, 255, 100), QColor(150, 150, 150)
        ]
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()

        task_label = QLabel("Задание:")
        self.task_combo = QComboBox()
        self._load_tasks()
        self.btn_load_task = QPushButton("Загрузить")
        self.btn_load_task.clicked.connect(self._load_selected_task)

        top_layout.addWidget(task_label)
        top_layout.addWidget(self.task_combo)
        top_layout.addWidget(self.btn_load_task)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        zoom_layout = QHBoxLayout()
        self.btn_zoom_out = QPushButton("-")
        self.btn_zoom_out.setToolTip("Уменьшить масштаб")
        self.btn_zoom_out.setMaximumWidth(40)
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setToolTip("Текущий масштаб")
        self.zoom_label.setMinimumWidth(50)
        
        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setToolTip("Увеличить масштаб")
        self.btn_zoom_in.setMaximumWidth(40)
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        
        self.btn_zoom_fit = QPushButton("Вписать")
        self.btn_zoom_fit.setToolTip("Масштабировать по размеру окна")
        self.btn_zoom_fit.clicked.connect(self._zoom_fit)

        zoom_layout.addWidget(self.btn_zoom_out)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_fit)
        zoom_layout.addStretch()

        layout.addLayout(zoom_layout)

        self.canvas = CanvasView(self)
        self.canvas.setMinimumHeight(400)
        layout.addWidget(self.canvas)

        nav_layout = QHBoxLayout()
        self.btn_prev_sheet = QPushButton("< Предыдущий лист")
        self.btn_next_sheet = QPushButton("Следующий лист >")
        self.sheet_label = QLabel("Лист: -")

        self.btn_prev_sheet.clicked.connect(self._prev_sheet)
        self.btn_next_sheet.clicked.connect(self._next_sheet)

        nav_layout.addWidget(self.btn_prev_sheet)
        nav_layout.addWidget(self.sheet_label)
        nav_layout.addWidget(self.btn_next_sheet)

        layout.addLayout(nav_layout)

        info_layout = QHBoxLayout()
        self.info_label = QLabel("КИМ: - | Деталей: -")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()

        layout.addLayout(info_layout)

        export_layout = QHBoxLayout()
        self.btn_export_pdf = QPushButton("Экспорт в PDF")
        self.btn_export_png = QPushButton("Экспорт в PNG")
        self.btn_export_label = QPushButton("Этикетки")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_export_pdf.clicked.connect(self._export_pdf)
        self.btn_export_png.clicked.connect(self._export_png)
        self.btn_export_label.clicked.connect(self._export_labels)
        self.btn_refresh.clicked.connect(self._load_tasks)

        export_layout.addWidget(self.btn_export_pdf)
        export_layout.addWidget(self.btn_export_png)
        export_layout.addWidget(self.btn_export_label)
        export_layout.addWidget(self.btn_refresh)

        layout.addLayout(export_layout)

        summary_table = QTableWidget()
        summary_table.setColumnCount(5)
        summary_table.setHorizontalHeaderLabels(["Лист", "Деталь", "Позиция X", "Позиция Y", "Размеры"])
        self.summary_table = summary_table
        layout.addWidget(summary_table)

    def _load_tasks(self):
        current_task_id = self.task_combo.currentData()
        self.task_combo.clear()
        tasks = self.job_service.get_all_tasks()
        for t in tasks:
            self.task_combo.addItem(f"{t.id} - {t.order_id} ({t.status})", t.id)
        if current_task_id is not None:
            idx = self.task_combo.findData(current_task_id)
            if idx >= 0:
                self.task_combo.setCurrentIndex(idx)

    def refresh_data(self):
        self._load_tasks()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_tasks()

    def _load_selected_task(self):
        task_id = self.task_combo.currentData()
        if task_id is None:
            QMessageBox.warning(self, "Внимание", "Выберите задание из списка")
            return

        self._current_task = self.job_service.get_task(task_id)
        if not self._current_task:
            QMessageBox.warning(self, "Внимание", "Задание не найдено")
            return

        self._current_sheet_index = 0
        if not self._draw_current_sheet():
            QMessageBox.information(
                self,
                "Информация",
                "Для выбранного задания пока нет сохраненных листов раскроя.",
            )

    def _draw_current_sheet(self):
        if not self._current_task:
            return False

        task_sheets = self.job_service.get_task_sheets(self._current_task.id)
        if not task_sheets or self._current_sheet_index >= len(task_sheets):
            self.canvas.clear_canvas()
            self.sheet_label.setText("Лист: -")
            self.info_label.setText("КИМ: - | Деталей на листе: -")
            self.summary_table.setRowCount(0)
            self.btn_prev_sheet.setEnabled(False)
            self.btn_next_sheet.setEnabled(False)
            return False

        current_ts = task_sheets[self._current_sheet_index]
        stock_sheet = current_ts.stock_sheet

        self.canvas.clear_canvas()
        self.canvas.draw_sheet(stock_sheet.format.width_mm, stock_sheet.format.height_mm, self._current_sheet_index)

        placements = self.session.query(Placement).filter(Placement.task_sheet_id == current_ts.id).all()

        self.summary_table.setRowCount(len(placements))
        for i, pl in enumerate(placements):
            order_item = pl.order_item
            color_idx = i % len(self._colors)

            self.canvas.add_piece(
                pl.x_mm, pl.y_mm,
                pl.width_mm, pl.height_mm,
                order_item.name if order_item else f"Detail {i+1}",
                self._colors[color_idx]
            )

            self.summary_table.setItem(i, 0, QTableWidgetItem(str(self._current_sheet_index + 1)))
            self.summary_table.setItem(i, 1, QTableWidgetItem(order_item.name if order_item else ""))
            self.summary_table.setItem(i, 2, QTableWidgetItem(f"{pl.x_mm:.1f}"))
            self.summary_table.setItem(i, 3, QTableWidgetItem(f"{pl.y_mm:.1f}"))
            self.summary_table.setItem(i, 4, QTableWidgetItem(f"{pl.width_mm}x{pl.height_mm}"))

        self.summary_table.resizeColumnsToContents()

        total_sheets = len(task_sheets)
        total_placements = len(placements)
        kim = self._current_task.kim_percent or 0

        self.sheet_label.setText(f"Лист: {self._current_sheet_index + 1} из {total_sheets}")
        self.info_label.setText(f"КИМ: {kim:.2f}% | Деталей на листе: {total_placements}")

        self.btn_prev_sheet.setEnabled(self._current_sheet_index > 0)
        self.btn_next_sheet.setEnabled(self._current_sheet_index < total_sheets - 1)
        return True

    def _prev_sheet(self):
        if not self._current_task:
            QMessageBox.warning(self, "Внимание", "Сначала загрузите задание")
            return
        if self._current_sheet_index > 0:
            self._current_sheet_index -= 1
            self._draw_current_sheet()

    def _next_sheet(self):
        if not self._current_task:
            QMessageBox.warning(self, "Внимание", "Сначала загрузите задание")
            return
        task_sheets = self.job_service.get_task_sheets(self._current_task.id)
        if self._current_sheet_index < len(task_sheets) - 1:
            self._current_sheet_index += 1
            self._draw_current_sheet()

    def _export_pdf(self):
        if not self._current_task:
            QMessageBox.warning(self, "Внимание", "Загрузите задание")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", "", "PDF Files (*.pdf)")
        if path:
            task_sheets = self.job_service.get_task_sheets(self._current_task.id)
            task_info = {"order_number": self._current_task.order_id, "kim_percent": self._current_task.kim_percent}
            self.export_service.export_to_pdf(task_sheets, path, task_info)
            QMessageBox.information(self, "Успех", f"Сохранено: {path}")

    def _export_png(self):
        if not self._current_task:
            QMessageBox.warning(self, "Внимание", "Загрузите задание")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Сохранить PNG", "", "PNG Files (*.png)")
        if path:
            task_sheets = self.job_service.get_task_sheets(self._current_task.id)
            if self._current_sheet_index < len(task_sheets):
                self.export_service.export_to_png(task_sheets[self._current_sheet_index], path)
                QMessageBox.information(self, "Успех", f"Сохранено: {path}")

    def _export_labels(self):
        if not self._current_task:
            QMessageBox.warning(self, "Внимание", "Загрузите задание")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Сохранить этикетки", "", "PDF Files (*.pdf)")
        if not path:
            return

        task_sheets = self.job_service.get_task_sheets(self._current_task.id)
        generated = 0
        for ts in task_sheets:
            placements = self.session.query(Placement).filter(Placement.task_sheet_id == ts.id).all()
            for idx, pl in enumerate(placements, start=1):
                item = pl.order_item
                if not item:
                    continue
                label_path = path.replace(".pdf", f"_sheet{ts.sheet_index + 1}_item{idx}.pdf")
                self.export_service.generate_label(
                    piece_name=item.name,
                    dimensions=f"{pl.width_mm}x{pl.height_mm}",
                    order_number=self._current_task.order_id,
                    output_path=label_path,
                )
                generated += 1

        QMessageBox.information(self, "Успех", f"Сгенерировано этикеток: {generated}")

    def _zoom_in(self):
        if hasattr(self.canvas, '_zoom'):
            self.canvas._zoom = min(self.canvas._zoom * 1.2, 5.0)
            self.canvas.scale(1.2, 1.2)
            self._update_zoom_label()

    def _zoom_out(self):
        if hasattr(self.canvas, '_zoom'):
            self.canvas._zoom = max(self.canvas._zoom / 1.2, 0.2)
            self.canvas.scale(0.8, 0.8)
            self._update_zoom_label()

    def _zoom_fit(self):
        if hasattr(self.canvas, 'zoom_fit'):
            self.canvas.zoom_fit()
            self.canvas._zoom = 1.0
            self._update_zoom_label()

    def _update_zoom_label(self):
        zoom_percent = int(getattr(self.canvas, '_zoom', 1.0) * 100)
        self.zoom_label.setText(f"{zoom_percent}%")
