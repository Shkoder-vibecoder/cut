from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QLabel, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from db.models import Order, OrderItem
from utils.importer import Importer


class OrdersView(QWidget):
    def __init__(self, order_service, session):
        super().__init__()
        self.order_service = order_service
        self.session = session
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.btn_create_order = QPushButton("Создать заказ")
        self.btn_edit_order = QPushButton("Редактировать заказ")
        self.btn_delete_order = QPushButton("Удалить заказ")
        self.btn_import = QPushButton("Импорт CSV/Excel")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_add_item = QPushButton("Добавить позицию")
        self.btn_view_items = QPushButton("Просмотр позиций")

        self.btn_create_order.clicked.connect(self._create_order)
        self.btn_edit_order.clicked.connect(self._edit_order)
        self.btn_delete_order.clicked.connect(self._delete_order)
        self.btn_import.clicked.connect(self._import_spec)
        self.btn_refresh.clicked.connect(self._refresh_orders)
        self.btn_add_item.clicked.connect(self._add_item)
        self.btn_view_items.clicked.connect(self._view_items)

        btn_layout.addWidget(self.btn_create_order)
        btn_layout.addWidget(self.btn_edit_order)
        btn_layout.addWidget(self.btn_delete_order)
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_add_item)
        btn_layout.addWidget(self.btn_view_items)

        layout.addLayout(btn_layout)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Номер заказа", "Клиент", "Статус", "Создан", "Обновлён"])
        layout.addWidget(self.orders_table)

        self._refresh_orders()

    def _refresh_orders(self):
        orders = self.order_service.get_all_orders()
        self.orders_table.setRowCount(len(orders))
        for i, o in enumerate(orders):
            self.orders_table.setItem(i, 0, QTableWidgetItem(o.order_number))
            self.orders_table.setItem(i, 1, QTableWidgetItem(o.client or ""))
            self.orders_table.setItem(i, 2, QTableWidgetItem(o.status))
            self.orders_table.setItem(i, 3, QTableWidgetItem(str(o.created_at)))
            self.orders_table.setItem(i, 4, QTableWidgetItem(str(o.updated_at)))
        self.orders_table.resizeColumnsToContents()

    def _create_order(self):
        dialog = OrderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            order_number = dialog.order_number_input.text()
            client = dialog.client_input.text()
            self.order_service.create_order(order_number, client)
            self._refresh_orders()

    def _edit_order(self):
        row = self.orders_table.currentRow()
        if row < 0:
            return
        order_number = self.orders_table.item(row, 0).text()
        order = self.order_service.get_order(order_number)
        if not order:
            return

        dialog = OrderDialog(self, order)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.order_service.update_order(order_number, client=dialog.client_input.text())
            self._refresh_orders()

    def _delete_order(self):
        row = self.orders_table.currentRow()
        if row < 0:
            return
        order_number = self.orders_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Подтверждение", "Удалить заказ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.order_service.delete_order(order_number)
            self._refresh_orders()

    def _import_spec(self):
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите заказ для импорта")
            return

        order_number = self.orders_table.item(row, 0).text()
        file_path, _ = QFileDialog.getOpenFileName(self, "Импорт спецификации", "", "CSV Files (*.csv);;Excel Files (*.xlsx)")
        if not file_path:
            return

        try:
            importer = Importer()
            if file_path.endswith('.csv'):
                items_data = importer.import_csv(file_path)
            else:
                items_data = importer.import_excel(file_path)

            self.order_service.import_items_from_dict(order_number, items_data)
            QMessageBox.information(self, "Импорт", f"Импортировано {len(items_data)} позиций")
            self._refresh_orders()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _add_item(self):
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите заказ")
            return

        order_number = self.orders_table.item(row, 0).text()
        dialog = OrderItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            material_type_id = dialog.material_combo.currentData()
            name = dialog.name_input.text()
            width = float(dialog.width_input.text())
            height = float(dialog.height_input.text())
            quantity = dialog.quantity_spin.value()
            rotation = dialog.rotation_check.isChecked()
            fibers = dialog.fibers_combo.currentText()
            priority = dialog.priority_spin.value()

            self.order_service.add_order_item(order_number, material_type_id, name, width, height, quantity, rotation, fibers, priority)
            QMessageBox.information(self, "Успех", "Позиция добавлена")

    def _view_items(self):
        row = self.orders_table.currentRow()
        if row < 0:
            return
        order_number = self.orders_table.item(row, 0).text()
        dialog = ItemsDialog(self.order_service, order_number)
        dialog.exec()


class OrderDialog(QDialog):
    def __init__(self, parent, order=None):
        super().__init__(parent)
        self.setWindowTitle("Заказ" if not order else "Редактирование заказа")
        layout = QFormLayout(self)

        self.order_number_input = QLineEdit()
        self.order_number_input.setToolTip("Введите уникальный номер заказа")
        self.client_input = QLineEdit()
        self.client_input.setToolTip("Введите название клиента или организации")

        if order:
            self.order_number_input.setText(order.order_number)
            self.order_number_input.setReadOnly(True)
            self.client_input.setText(order.client or "")

        layout.addRow("Номер заказа:", self.order_number_input)
        layout.addRow("Клиент:", self.client_input)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("ОК")
        btn_cancel = QPushButton("Отмена")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)


class OrderItemDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Позиция заказа")
        layout = QFormLayout(self)

        from db.session import get_session
        from core.material_service import MaterialService
        session = get_session()
        material_service = MaterialService(session)

        self.name_input = QLineEdit()
        self.name_input.setToolTip("Введите название детали (например: Фасад шкафа)")
        self.width_input = QLineEdit()
        self.width_input.setToolTip("Введите ширину детали в миллиметрах")
        self.height_input = QLineEdit()
        self.height_input.setToolTip("Введите высоту детали в миллиметрах")

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 10000)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setToolTip("Введите количество деталей данного типа")

        self.material_combo = QComboBox()
        self.material_combo.setToolTip("Выберите тип материала для детали")
        materials = material_service.get_all_material_types()
        for m in materials:
            self.material_combo.addItem(m.name, m.id)

        self.rotation_check = QComboBox()
        self.rotation_check.setToolTip("Разрешено ли вращение детали при раскрое")
        self.rotation_check.addItems(["Да", "Нет"])

        self.fibers_combo = QComboBox()
        self.fibers_combo.setToolTip("Выберите требуемое направление волокон")
        self.fibers_combo.addItems(["any", "horizontal", "vertical"])

        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(0, 100)
        self.priority_spin.setValue(0)

        layout.addRow("Название:", self.name_input)
        layout.addRow("Материал:", self.material_combo)
        layout.addRow("Ширина, мм:", self.width_input)
        layout.addRow("Высота, мм:", self.height_input)
        layout.addRow("Количество:", self.quantity_spin)
        layout.addRow("Вращение:", self.rotation_check)
        layout.addRow("Волокна:", self.fibers_combo)
        layout.addRow("Приоритет:", self.priority_spin)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("ОК")
        btn_cancel = QPushButton("Отмена")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)


class ItemsDialog(QDialog):
    def __init__(self, order_service, order_number):
        super().__init__()
        self.setWindowTitle(f"Позиции заказа: {order_number}")
        self.resize(700, 400)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Материал", "Ширина", "Высота", "Кол-во", "Вращение", "Волокна"])
        layout.addWidget(self.table)

        items = order_service.get_order_items(order_number)
        self.table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.table.setItem(i, 1, QTableWidgetItem(item.name))
            self.table.setItem(i, 2, QTableWidgetItem(item.material_type.name if item.material_type else ""))
            self.table.setItem(i, 3, QTableWidgetItem(str(item.width_mm)))
            self.table.setItem(i, 4, QTableWidgetItem(str(item.height_mm)))
            self.table.setItem(i, 5, QTableWidgetItem(str(item.quantity)))
            self.table.setItem(i, 6, QTableWidgetItem("Да" if item.rotation else "Нет"))
            self.table.setItem(i, 7, QTableWidgetItem(item.fibers))
        self.table.resizeColumnsToContents()

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)