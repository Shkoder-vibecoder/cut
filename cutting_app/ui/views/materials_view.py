from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox, QLabel, QMessageBox, QTabWidget, QHeaderView
from PyQt6.QtCore import Qt
from db.models import MaterialType, SheetFormat


class MaterialsView(QWidget):
    def __init__(self, material_service, session):
        super().__init__()
        self.material_service = material_service
        self.session = session
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_materials_tab(), "Типы материалов")
        self.tab_widget.addTab(self._create_formats_tab(), "Форматы листов")

        layout.addWidget(self.tab_widget)

    def _create_materials_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        btn_layout = QHBoxLayout()
        self.btn_add_material = QPushButton("Добавить")
        self.btn_delete_material = QPushButton("Удалить выбранные")
        self.btn_refresh_materials = QPushButton("Обновить")

        self.btn_add_material.clicked.connect(self._add_material)
        self.btn_delete_material.clicked.connect(self._delete_selected_materials)
        self.btn_refresh_materials.clicked.connect(self._refresh_materials)

        btn_layout.addWidget(self.btn_add_material)
        btn_layout.addWidget(self.btn_delete_material)
        btn_layout.addWidget(self.btn_refresh_materials)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(3)
        self.materials_table.setHorizontalHeaderLabels(["ID", "Название", "Описание"])
        self.materials_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.materials_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.materials_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.materials_table)

        self._refresh_materials()
        return widget

    def _create_formats_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        btn_layout = QHBoxLayout()
        self.btn_add_format = QPushButton("Добавить формат")
        self.btn_delete_format = QPushButton("Удалить выбранные")
        self.btn_refresh_formats = QPushButton("Обновить")

        self.btn_add_format.clicked.connect(self._add_format)
        self.btn_delete_format.clicked.connect(self._delete_selected_formats)
        self.btn_refresh_formats.clicked.connect(self._refresh_formats)

        btn_layout.addWidget(self.btn_add_format)
        btn_layout.addWidget(self.btn_delete_format)
        btn_layout.addWidget(self.btn_refresh_formats)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.formats_table = QTableWidget()
        self.formats_table.setColumnCount(7)
        self.formats_table.setHorizontalHeaderLabels(["", "ID", "Материал", "Название", "Ширина, мм", "Высота, мм", "Толщина, мм"])
        self.formats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.formats_table)

        self._refresh_formats()
        return widget

    def _refresh_materials(self):
        materials = self.material_service.get_all_material_types()
        self.materials_table.setRowCount(len(materials))
        for i, m in enumerate(materials):
            self.materials_table.setItem(i, 0, QTableWidgetItem(str(m.id)))
            self.materials_table.setItem(i, 1, QTableWidgetItem(m.name))
            self.materials_table.setItem(i, 2, QTableWidgetItem(m.description or ""))
        self.materials_table.resizeColumnsToContents()

    def _refresh_formats(self):
        formats = self.material_service.get_all_formats()
        self.formats_table.setRowCount(len(formats))
        for i, f in enumerate(formats):
            self.formats_table.setItem(i, 0, QTableWidgetItem(str(f.id)))
            self.formats_table.setItem(i, 1, QTableWidgetItem(f.material_type.name if f.material_type else ""))
            self.formats_table.setItem(i, 2, QTableWidgetItem(f.name))
            self.formats_table.setItem(i, 3, QTableWidgetItem(str(f.width_mm)))
            self.formats_table.setItem(i, 4, QTableWidgetItem(str(f.height_mm)))
            self.formats_table.setItem(i, 5, QTableWidgetItem(str(f.thickness_mm or "")))
        self.formats_table.resizeColumnsToContents()

    def _delete_selected_materials(self):
        selected_ids = []
        for i in range(self.materials_table.rowCount()):
            if self.materials_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                selected_ids.append(int(self.materials_table.item(i, 1).text()))
        
        if not selected_ids:
            QMessageBox.warning(self, "Внимание", "Выберите материалы для удаления")
            return
            
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить {len(selected_ids)} материал(ов)?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for material_id in selected_ids:
                self.material_service.delete_material_type(material_id)
            self._refresh_materials()

    def _delete_selected_formats(self):
        selected_ids = []
        for i in range(self.formats_table.rowCount()):
            if self.formats_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                selected_ids.append(int(self.formats_table.item(i, 1).text()))
        
        if not selected_ids:
            QMessageBox.warning(self, "Внимание", "Выберите форматы для удаления")
            return
            
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить {len(selected_ids)} формат(ов)?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for format_id in selected_ids:
                self.material_service.delete_sheet_format(format_id)
            self._refresh_formats()

    def _add_material(self):
        dialog = MaterialDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_input.text()
            description = dialog.description_input.toPlainText()
            self.material_service.create_material_type(name, description)
            self._refresh_materials()

    def _edit_material(self):
        row = self.materials_table.currentRow()
        if row < 0:
            return
        material_id = int(self.materials_table.item(row, 0).text())
        material = self.material_service.get_material_type(material_id)
        if not material:
            return

        dialog = MaterialDialog(self, material)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.material_service.update_material_type(
                material_id,
                name=dialog.name_input.text(),
                description=dialog.description_input.toPlainText()
            )
            self._refresh_materials()

    def _add_format(self):
        dialog = FormatDialog(self, self.material_service.get_all_material_types())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            material_type_id = dialog.material_combo.currentData()
            name = dialog.name_input.text()
            width = float(dialog.width_input.text())
            height = float(dialog.height_input.text())
            thickness = float(dialog.thickness_input.text()) if dialog.thickness_input.text() else None
            self.material_service.create_sheet_format(material_type_id, name, width, height, thickness)
            self._refresh_formats()


class MaterialDialog(QDialog):
    def __init__(self, parent, material=None):
        super().__init__(parent)
        self.setWindowTitle("Материал" if not material else "Редактирование материала")
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setToolTip("Введите название материала (обязательное поле)")
        self.description_input = QTextEdit()
        self.description_input.setToolTip("Введите описание материала (необязательное поле)")

        if material:
            self.name_input.setText(material.name)
            self.description_input.setPlainText(material.description or "")

        layout.addRow("Название:", self.name_input)
        layout.addRow("Описание:", self.description_input)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("ОК")
        btn_cancel = QPushButton("Отмена")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)


class FormatDialog(QDialog):
    def __init__(self, parent, materials, format_obj=None):
        super().__init__(parent)
        self.setWindowTitle("Формат листа" if not format_obj else "Редактирование формата")
        layout = QFormLayout(self)

        self.material_combo = QComboBox()
        self.material_combo.setToolTip("Выберите тип материала из справочника")
        for m in materials:
            self.material_combo.addItem(m.name, m.id)

        self.name_input = QLineEdit()
        self.name_input.setToolTip("Введите название формата (например: ЛДСП 2800x2070)")
        self.width_input = QLineEdit()
        self.width_input.setToolTip("Введите ширину листа в миллиметрах (например: 2800)")
        self.height_input = QLineEdit()
        self.height_input.setToolTip("Введите высоту листа в миллиметрах (например: 2070)")
        self.thickness_input = QLineEdit()
        self.thickness_input.setToolTip("Введите толщину листа в миллиметрах (например: 16)")

        if format_obj:
            for i in range(self.material_combo.count()):
                if self.material_combo.itemData(i) == format_obj.material_type_id:
                    self.material_combo.setCurrentIndex(i)
                    break
            self.name_input.setText(format_obj.name)
            self.width_input.setText(str(format_obj.width_mm))
            self.height_input.setText(str(format_obj.height_mm))
            self.thickness_input.setText(str(format_obj.thickness_mm) if format_obj.thickness_mm else "")

        layout.addRow("Материал:", self.material_combo)
        layout.addRow("Название:", self.name_input)
        layout.addRow("Ширина, мм:", self.width_input)
        layout.addRow("Высота, мм:", self.height_input)
        layout.addRow("Толщина, мм:", self.thickness_input)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("ОК")
        btn_cancel = QPushButton("Отмена")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)