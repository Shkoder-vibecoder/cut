from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QDialog, QFormLayout, 
                             QLineEdit, QMessageBox, QLabel, QComboBox, QSpinBox,
                             QDoubleSpinBox, QCheckBox)
from PyQt6.QtCore import Qt
from db.models import OrderTemplate
import json


class TemplatesView(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton("Создать шаблон")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_apply = QPushButton("Применить к заказу")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_create.clicked.connect(self._create_template)
        self.btn_edit.clicked.connect(self._edit_template)
        self.btn_delete.clicked.connect(self._delete_template)
        self.btn_refresh.clicked.connect(self._refresh_templates)

        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.templates_table = QTableWidget()
        self.templates_table.setColumnCount(3)
        self.templates_table.setHorizontalHeaderLabels(["ID", "Название", "Позиций"])
        layout.addWidget(self.templates_table)

        self._refresh_templates()

    def _refresh_templates(self):
        templates = self.session.query(OrderTemplate).all()
        self.templates_table.setRowCount(len(templates))
        for i, t in enumerate(templates):
            self.templates_table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.templates_table.setItem(i, 1, QTableWidgetItem(t.name))
            positions = json.loads(t.positions_json) if isinstance(t.positions_json, str) else t.positions_json
            self.templates_table.setItem(i, 2, QTableWidgetItem(str(len(positions))))
        self.templates_table.resizeColumnsToContents()

    def _create_template(self):
        dialog = TemplateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_input.text()
            positions = dialog.get_positions()

            template = OrderTemplate(
                name=name,
                positions_json=json.dumps(positions)
            )
            self.session.add(template)
            self.session.commit()
            self._refresh_templates()

    def _edit_template(self):
        row = self.templates_table.currentRow()
        if row < 0:
            return

        template_id = int(self.templates_table.item(row, 0).text())
        template = self.session.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
        if not template:
            return

        dialog = TemplateDialog(self, template)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template.name = dialog.name_input.text()
            template.positions_json = json.dumps(dialog.get_positions())
            self.session.commit()
            self._refresh_templates()

    def _delete_template(self):
        row = self.templates_table.currentRow()
        if row < 0:
            return

        template_id = int(self.templates_table.item(row, 0).text())
        reply = QMessageBox.question(self, "Подтверждение", "Удалить шаблон?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            template = self.session.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
            if template:
                self.session.delete(template)
                self.session.commit()
                self._refresh_templates()


class TemplateDialog(QDialog):
    def __init__(self, parent, template=None):
        super().__init__(parent)
        self.setWindowTitle("Шаблон заказа" if not template else "Редактирование шаблона")
        self.template = template
        self._setup_ui()

        if template:
            self.name_input.setText(template.name)
            positions = json.loads(template.positions_json) if isinstance(template.positions_json, str) else template.positions_json
            for pos in positions:
                self._add_position_row(pos)

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input, 1)
        layout.addLayout(name_layout)

        positions_group = QWidget()
        positions_layout = QVBoxLayout(positions_group)

        self.positions_widget = QWidget()
        self.positions_layout = QVBoxLayout(self.positions_widget)
        self.position_rows = []

        btn_add_layout = QHBoxLayout()
        self.btn_add_position = QPushButton("Добавить позицию")
        self.btn_add_position.clicked.connect(self._add_position)
        btn_add_layout.addWidget(self.btn_add_position)
        btn_add_layout.addStretch()
        positions_layout.addWidget(self.positions_widget)
        positions_layout.addLayout(btn_add_layout)

        layout.addWidget(positions_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_ok = QPushButton("ОК")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _add_position(self, data=None):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        name = QLineEdit()
        width = QDoubleSpinBox()
        width.setRange(1, 10000)
        width.setSuffix(" мм")
        height = QDoubleSpinBox()
        height.setRange(1, 10000)
        height.setSuffix(" мм")
        qty = QSpinBox()
        qty.setRange(1, 10000)
        qty.setValue(1)
        rotation = QCheckBox("Вращение")
        rotation.setChecked(True)
        fibers = QComboBox()
        fibers.addItem("Любое", "any")
        fibers.addItem("Горизонтальное", "horizontal")
        fibers.addItem("Вертикальное", "vertical")

        if data:
            name.setText(data.get("name", ""))
            width.setValue(data.get("width_mm", 100))
            height.setValue(data.get("height_mm", 100))
            qty.setValue(data.get("quantity", 1))
            rotation.setChecked(data.get("rotation", True))
            idx = fibers.findData(data.get("fibers", "any"))
            if idx >= 0:
                fibers.setCurrentIndex(idx)

        row_layout.addWidget(name, 2)
        row_layout.addWidget(width, 1)
        row_layout.addWidget(height, 1)
        row_layout.addWidget(qty, 1)
        row_layout.addWidget(rotation)
        row_layout.addWidget(fibers)

        btn_remove = QPushButton("X")
        btn_remove.clicked.connect(lambda: self._remove_position(row_widget))
        row_layout.addWidget(btn_remove)

        self.positions_layout.addWidget(row_widget)
        self.position_rows.append({
            "widget": row_widget,
            "name": name,
            "width": width,
            "height": height,
            "qty": qty,
            "rotation": rotation,
            "fibers": fibers
        })

    def _add_position_row(self, data=None):
        self._add_position(data)

    def _remove_position(self, widget):
        for i, row in enumerate(self.position_rows):
            if row["widget"] == widget:
                self.positions_layout.removeWidget(widget)
                widget.deleteLater()
                self.position_rows.pop(i)
                break

    def get_positions(self) -> list:
        positions = []
        for row in self.position_rows:
            positions.append({
                "name": row["name"].text(),
                "width_mm": row["width"].value(),
                "height_mm": row["height"].value(),
                "quantity": row["qty"].value(),
                "rotation": row["rotation"].isChecked(),
                "fibers": row["fibers"].currentData(),
                "material_type_id": 1
            })
        return positions
