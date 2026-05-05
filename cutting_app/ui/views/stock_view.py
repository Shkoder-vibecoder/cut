from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from db.models import StockSheet


class StockView(QWidget):
    def __init__(self, stock_service, session):
        super().__init__()
        self.stock_service = stock_service
        self.session = session
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.btn_add_stock = QPushButton("Добавить на склад")
        self.btn_edit_stock = QPushButton("Редактировать")
        self.btn_write_off = QPushButton("Списать")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_movements = QPushButton("История движений")

        self.btn_add_stock.clicked.connect(self._add_stock)
        self.btn_edit_stock.clicked.connect(self._edit_stock)
        self.btn_write_off.clicked.connect(self._write_off)
        self.btn_refresh.clicked.connect(self._refresh_stock)
        self.btn_movements.clicked.connect(self._show_movements)

        btn_layout.addWidget(self.btn_add_stock)
        btn_layout.addWidget(self.btn_edit_stock)
        btn_layout.addWidget(self.btn_write_off)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_movements)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(8)
        self.stock_table.setHorizontalHeaderLabels(["ID", "Формат", "Текстура", "Цена", "Кол-во", "Дефекты", "Создан", "Использован"])
        layout.addWidget(self.stock_table)

        self._refresh_stock()

    def _refresh_stock(self):
        sheets = self.stock_service.get_all_stock_sheets()
        self.stock_table.setRowCount(len(sheets))
        for i, s in enumerate(sheets):
            self.stock_table.setItem(i, 0, QTableWidgetItem(str(s.id)))
            self.stock_table.setItem(i, 1, QTableWidgetItem(s.format.name if s.format else ""))
            self.stock_table.setItem(i, 2, QTableWidgetItem(s.texture))
            self.stock_table.setItem(i, 3, QTableWidgetItem(str(s.price)))
            self.stock_table.setItem(i, 4, QTableWidgetItem(str(s.quantity)))
            self.stock_table.setItem(i, 5, QTableWidgetItem(str(len(s.defects_json)) if s.defects_json else ""))
            self.stock_table.setItem(i, 6, QTableWidgetItem(str(s.created_at)))
            usage = len(s.task_sheets) if hasattr(s, 'task_sheets') else 0
            self.stock_table.setItem(i, 7, QTableWidgetItem(str(usage)))
        self.stock_table.resizeColumnsToContents()

    def _add_stock(self):
        dialog = StockDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            format_id = dialog.format_combo.currentData()
            texture = dialog.texture_combo.currentText()
            price = dialog.price_spin.value()
            quantity = dialog.quantity_spin.value()
            self.stock_service.add_stock_sheet(format_id, texture, price, quantity)
            self._refresh_stock()

    def _edit_stock(self):
        row = self.stock_table.currentRow()
        if row < 0:
            return
        sheet_id = int(self.stock_table.item(row, 0).text())
        sheet = self.stock_service.get_stock_sheet(sheet_id)
        if not sheet:
            return

        dialog = StockDialog(self, sheet)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            format_id = dialog.format_combo.currentData()
            texture = dialog.texture_combo.currentText()
            price = dialog.price_spin.value()
            quantity = dialog.quantity_spin.value()
            self.stock_service.update_stock_sheet(sheet_id, quantity=quantity, price=price, texture=texture)
            self._refresh_stock()

    def _write_off(self):
        row = self.stock_table.currentRow()
        if row < 0:
            return
        sheet_id = int(self.stock_table.item(row, 0).text())
        reply = QMessageBox.question(self, "Подтверждение", "Списать 1 лист?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.stock_service.adjust_quantity(sheet_id, -1, reason="manual")
            self._refresh_stock()

    def _show_movements(self):
        dialog = MovementsDialog(self.stock_service)
        dialog.exec()


class StockDialog(QDialog):
    def __init__(self, parent, stock_sheet=None):
        super().__init__(parent)
        self.setWindowTitle("Склад")
        from core.stock_service import StockService
        from db.session import get_session

        layout = QFormLayout(self)

        session = get_session()
        from core.material_service import MaterialService
        material_service = MaterialService(session)

        self.format_combo = QComboBox()
        self.format_combo.setToolTip("Выберите формат листа из справочника")
        formats = material_service.get_all_formats()
        for f in formats:
            self.format_combo.addItem(f"{f.name} ({f.width_mm}x{f.height_mm})", f.id)

        self.texture_combo = QComboBox()
        self.texture_combo.setToolTip("Выберите направление текстуры/волокон")
        self.texture_combo.addItems(["none", "horizontal", "vertical"])

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 100000)
        self.price_spin.setDecimals(2)
        self.price_spin.setToolTip("Введите цену за лист в рублях")

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 10000)
        self.quantity_spin.setToolTip("Введите количество листов")
        self.quantity_spin.setValue(1)

        if stock_sheet:
            for i in range(self.format_combo.count()):
                if self.format_combo.itemData(i) == stock_sheet.format_id:
                    self.format_combo.setCurrentIndex(i)
                    break
            idx = self.texture_combo.findText(stock_sheet.texture)
            if idx >= 0:
                self.texture_combo.setCurrentIndex(idx)
            self.price_spin.setValue(stock_sheet.price)
            self.quantity_spin.setValue(stock_sheet.quantity)

        layout.addRow("Формат:", self.format_combo)
        layout.addRow("Текстура:", self.texture_combo)
        layout.addRow("Цена:", self.price_spin)
        layout.addRow("Количество:", self.quantity_spin)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("ОК")
        btn_cancel = QPushButton("Отмена")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)


class MovementsDialog(QDialog):
    def __init__(self, stock_service):
        super().__init__()
        self.setWindowTitle("История движений склада")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Лист", "Дельта", "Причина", "Дата"])
        layout.addWidget(self.table)

        movements = stock_service.get_movements()
        self.table.setRowCount(len(movements))
        for i, m in enumerate(movements):
            self.table.setItem(i, 0, QTableWidgetItem(str(m.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(m.stock_sheet_id)))
            self.table.setItem(i, 2, QTableWidgetItem(str(m.delta)))
            self.table.setItem(i, 3, QTableWidgetItem(m.reason))
            self.table.setItem(i, 4, QTableWidgetItem(str(m.created_at)))
        self.table.resizeColumnsToContents()

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)