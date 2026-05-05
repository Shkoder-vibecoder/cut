from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox, 
                             QCheckBox, QGroupBox, QFormLayout, QComboBox)
from PyQt6.QtCore import Qt
from config import (DEFAULT_CUT_WIDTH, DEFAULT_EDGE_OFFSET, GA_POPULATION_SIZE, 
                    GA_GENERATIONS, GA_MUTATION_RATE, SA_INITIAL_TEMP, SA_COOLING_RATE,
                    AUTO_SAVE_INTERVAL)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        cutting_group = QGroupBox("Параметры раскроя")
        cutting_layout = QFormLayout()

        self.cut_width = QDoubleSpinBox()
        self.cut_width.setRange(0.1, 20.0)
        self.cut_width.setValue(DEFAULT_CUT_WIDTH)
        self.cut_width.setSuffix(" мм")
        cutting_layout.addRow("Ширина реза:", self.cut_width)

        self.edge_offset = QDoubleSpinBox()
        self.edge_offset.setRange(0, 50.0)
        self.edge_offset.setValue(DEFAULT_EDGE_OFFSET)
        self.edge_offset.setSuffix(" мм")
        cutting_layout.addRow("Отступ от края:", self.edge_offset)

        cutting_group.setLayout(cutting_layout)
        layout.addWidget(cutting_group)

        ga_group = QGroupBox("Генетический алгоритм")
        ga_layout = QFormLayout()

        self.ga_population = QSpinBox()
        self.ga_population.setRange(10, 200)
        self.ga_population.setValue(GA_POPULATION_SIZE)
        ga_layout.addRow("Размер популяции:", self.ga_population)

        self.ga_generations = QSpinBox()
        self.ga_generations.setRange(10, 1000)
        self.ga_generations.setValue(GA_GENERATIONS)
        ga_layout.addRow("Число поколений:", self.ga_generations)

        self.ga_mutation = QDoubleSpinBox()
        self.ga_mutation.setRange(0.01, 0.5)
        self.ga_mutation.setDecimals(2)
        self.ga_mutation.setValue(GA_MUTATION_RATE)
        ga_layout.addRow("Мутация:", self.ga_mutation)

        ga_group.setLayout(ga_layout)
        layout.addWidget(ga_group)

        sa_group = QGroupBox("Имитация отжига")
        sa_layout = QFormLayout()

        self.sa_initial_temp = QDoubleSpinBox()
        self.sa_initial_temp.setRange(100, 5000)
        self.sa_initial_temp.setValue(SA_INITIAL_TEMP)
        sa_layout.addRow("Начальная температура:", self.sa_initial_temp)

        self.sa_cooling = QDoubleSpinBox()
        self.sa_cooling.setRange(0.9, 0.999)
        self.sa_cooling.setDecimals(3)
        self.sa_cooling.setValue(SA_COOLING_RATE)
        sa_layout.addRow("Коэффициент охлаждения:", self.sa_cooling)

        sa_group.setLayout(sa_layout)
        layout.addWidget(sa_group)

        system_group = QGroupBox("Система")
        system_layout = QFormLayout()

        self.auto_save = QSpinBox()
        self.auto_save.setRange(60, 3600)
        self.auto_save.setValue(AUTO_SAVE_INTERVAL)
        self.auto_save.setSuffix(" сек")
        system_layout.addRow("Автосохранение:", self.auto_save)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_ok = QPushButton("Сохранить")
        self.btn_ok.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.btn_ok)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def _save_settings(self):
        self.accept()

    def get_settings(self) -> dict:
        return {
            "cut_width": self.cut_width.value(),
            "edge_offset": self.edge_offset.value(),
            "ga_population": self.ga_population.value(),
            "ga_generations": self.ga_generations.value(),
            "ga_mutation": self.ga_mutation.value(),
            "sa_initial_temp": self.sa_initial_temp.value(),
            "sa_cooling": self.sa_cooling.value(),
            "auto_save_interval": self.auto_save.value()
        }

    def set_settings(self, settings: dict):
        if "cut_width" in settings:
            self.cut_width.setValue(settings["cut_width"])
        if "edge_offset" in settings:
            self.edge_offset.setValue(settings["edge_offset"])
        if "ga_population" in settings:
            self.ga_population.setValue(settings["ga_population"])
        if "ga_generations" in settings:
            self.ga_generations.setValue(settings["ga_generations"])
        if "ga_mutation" in settings:
            self.ga_mutation.setValue(settings["ga_mutation"])
        if "sa_initial_temp" in settings:
            self.sa_initial_temp.setValue(settings["sa_initial_temp"])
        if "sa_cooling" in settings:
            self.sa_cooling.setValue(settings["sa_cooling"])
        if "auto_save_interval" in settings:
            self.auto_save.setValue(settings["auto_save_interval"])