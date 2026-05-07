from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QMessageBox,
    QProgressBar,
    QFormLayout,
)
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from algorithms.base import CuttingParams, Sheet, Piece
from algorithms.greedy import GreedyAlgorithm
from algorithms.genetic import GeneticAlgorithm
from algorithms.annealing import AnnealingAlgorithm
from config import MAX_CUTTING_PIECES, MAX_CUTTING_TIME_SECONDS, DEFAULT_EDGE_OFFSET
from ui.localization import ALGORITHM_LABELS, TASK_STATUS_LABELS


class AlgorithmWorker(QObject):
    finished = pyqtSignal(object, float)
    failed = pyqtSignal(str)

    def __init__(self, algo, sheets, pieces, params):
        super().__init__()
        self.algo = algo
        self.sheets = sheets
        self.pieces = pieces
        self.params = params

    def run(self):
        try:
            import time

            start_time = time.time()
            result = self.algo.solve(self.sheets, self.pieces, self.params)
            calc_time = time.time() - start_time
            self.finished.emit(result, calc_time)
        except Exception as exc:
            self.failed.emit(str(exc))


class JobView(QWidget):
    def __init__(self, job_service, order_service, stock_service, session):
        super().__init__()
        self.job_service = job_service
        self.order_service = order_service
        self.stock_service = stock_service
        self.session = session
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        order_label = QLabel("Заказ:")
        self.order_combo = QComboBox()
        self._load_orders()
        self.btn_refresh_orders = QPushButton("Обновить")
        self.btn_refresh_orders.clicked.connect(self._load_orders)
        top_layout.addWidget(order_label)
        top_layout.addWidget(self.order_combo)
        top_layout.addWidget(self.btn_refresh_orders)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        params_group = QWidget()
        params_layout = QFormLayout(params_group)

        self.cut_type_combo = QComboBox()
        self.cut_type_combo.addItem("Свободный", "free")
        self.cut_type_combo.addItem("Гильотинный", "guillotine")
        self.cut_type_combo.setToolTip("Тип схемы раскроя")

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItem("Жадный", "greedy")
        self.algorithm_combo.addItem("Генетический", "genetic")
        self.algorithm_combo.addItem("Отжиг", "annealing")
        self.algorithm_combo.setToolTip("Алгоритм оптимизации")

        self.cut_width_spin = QDoubleSpinBox()
        self.cut_width_spin.setRange(0.1, 20.0)
        self.cut_width_spin.setValue(3.0)
        self.cut_width_spin.setSuffix(" мм")
        self.cut_width_spin.setToolTip("Ширина технологического реза")

        self.edge_offset_spin = QDoubleSpinBox()
        self.edge_offset_spin.setRange(0, 50.0)
        self.edge_offset_spin.setValue(DEFAULT_EDGE_OFFSET)
        self.edge_offset_spin.setSuffix(" мм")
        self.edge_offset_spin.setToolTip("Минимальный отступ деталей от края листа")

        self.guillotine_depth_spin = QDoubleSpinBox()
        self.guillotine_depth_spin.setRange(1.0, 10000.0)
        self.guillotine_depth_spin.setValue(3000.0)
        self.guillotine_depth_spin.setSuffix(" мм")
        self.guillotine_depth_spin.setToolTip("Максимальная глубина гильотинного реза")

        params_layout.addRow("Тип раскроя:", self.cut_type_combo)
        params_layout.addRow("Алгоритм:", self.algorithm_combo)
        params_layout.addRow("Ширина реза:", self.cut_width_spin)
        params_layout.addRow("Отступ от края:", self.edge_offset_spin)
        params_layout.addRow("Глубина гильотины:", self.guillotine_depth_spin)
        layout.addWidget(params_group)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Рассчитать раскрой")
        self.btn_view_result = QPushButton("Просмотр результата")
        self.btn_tasks_history = QPushButton("История заданий")
        self.btn_start.clicked.connect(self._start_cutting)
        self.btn_view_result.clicked.connect(self._view_result)
        self.btn_tasks_history.clicked.connect(self._show_tasks_history)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_view_result)
        btn_layout.addWidget(self.btn_tasks_history)
        layout.addLayout(btn_layout)

        self.status_label = QLabel("Выберите заказ и нажмите 'Рассчитать раскрой'")
        layout.addWidget(self.status_label)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(
            ["ID", "Заказ", "Алгоритм", "КИМ %", "Статус", "Время"]
        )
        layout.addWidget(self.results_table)
        self._load_tasks()

    def _load_orders(self):
        self.order_combo.clear()
        for order in self.order_service.get_all_orders():
            self.order_combo.addItem(order.order_number, order.order_number)

    def _load_tasks(self):
        tasks = self.job_service.get_all_tasks()
        self.results_table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(task.id)))
            self.results_table.setItem(i, 1, QTableWidgetItem(task.order_id))
            self.results_table.setItem(
                i, 2, QTableWidgetItem(ALGORITHM_LABELS.get(task.algorithm, task.algorithm))
            )
            self.results_table.setItem(
                i, 3, QTableWidgetItem(f"{task.kim_percent:.2f}" if task.kim_percent else "-")
            )
            self.results_table.setItem(
                i, 4, QTableWidgetItem(TASK_STATUS_LABELS.get(task.status, task.status))
            )
            calc_time = str(task.completed_at - task.created_at) if task.completed_at else "-"
            self.results_table.setItem(i, 5, QTableWidgetItem(calc_time))
        self.results_table.resizeColumnsToContents()

    def _start_cutting(self):
        order_number = self.order_combo.currentData()
        if not order_number:
            QMessageBox.warning(self, "Внимание", "Выберите заказ")
            return

        items = self.order_service.get_order_items(order_number)
        if not items:
            QMessageBox.warning(self, "Внимание", "В заказе нет позиций")
            return

        stock_sheets = self.stock_service.get_all_stock_sheets()
        if not stock_sheets:
            QMessageBox.warning(self, "Внимание", "Нет листов на складе")
            return

        sheets = []
        for stock in stock_sheets:
            if stock.quantity > 0:
                sheets.append(
                    Sheet(
                        id=stock.id,
                        width=stock.format.width_mm,
                        height=stock.format.height_mm,
                        stock_sheet_id=stock.id,
                        texture=stock.texture,
                        quantity=stock.quantity,
                    )
                )

        pieces = []
        for item in items:
            for _ in range(item.quantity):
                pieces.append(
                    Piece(
                        id=item.id,
                        order_item_id=item.id,
                        name=item.name,
                        width=item.width_mm,
                        height=item.height_mm,
                        rotation_allowed=item.rotation,
                        fibers=item.fibers,
                        priority=item.priority,
                    )
                )

        params = CuttingParams(
            cut_width=self.cut_width_spin.value(),
            edge_offset=self.edge_offset_spin.value(),
            cut_type=self.cut_type_combo.currentData(),
            algorithm=self.algorithm_combo.currentData(),
            max_guillotine_depth=self.guillotine_depth_spin.value(),
        )

        if len(pieces) > MAX_CUTTING_PIECES:
            QMessageBox.warning(
                self,
                "Ограничение расчета",
                (
                    f"Слишком большой заказ: {len(pieces)} деталей. "
                    f"Максимум для стабильного расчета: {MAX_CUTTING_PIECES}."
                ),
            )
            return

        if params.algorithm in ("genetic", "annealing"):
            params.time_limit_seconds = float(MAX_CUTTING_TIME_SECONDS)
            if params.algorithm == "genetic" and len(pieces) > 120:
                params.population_size = min(params.population_size, 30)
                params.generations = min(params.generations, 80)

        self.progress_bar.setValue(10)
        self.status_label.setText(
            f"Запуск алгоритма... (лимит {int(params.time_limit_seconds or 0)} сек)"
            if params.time_limit_seconds
            else "Запуск алгоритма..."
        )
        self.btn_start.setEnabled(False)
        self._run_algorithm(sheets, pieces, params, order_number)

    def _run_algorithm(self, sheets, pieces, params, order_number):
        algo_name = params.algorithm
        if algo_name == "greedy":
            algo = GreedyAlgorithm()
        elif algo_name == "genetic":
            algo = GeneticAlgorithm()
        elif algo_name == "annealing":
            algo = AnnealingAlgorithm()
        else:
            algo = GreedyAlgorithm()

        from datetime import datetime
        from db.models import TaskSheet, Placement, StockSheet, InventoryMovement, TaskOrderItemLink

        self.progress_bar.setValue(30)
        self.status_label.setText("Выполняется оптимизация...")

        self._worker_thread = QThread(self)
        self._worker = AlgorithmWorker(algo, sheets, pieces, params)
        self._worker.moveToThread(self._worker_thread)

        def on_finished(result, calc_time):
            self.progress_bar.setValue(80)
            self.status_label.setText("Сохранение результата...")

            task = self.job_service.create_task(
                order_id=order_number,
                cut_width=params.cut_width,
                algorithm=params.algorithm,
                cut_type=params.cut_type,
            )

            sheet_map = {}
            for placement in result.placements:
                if placement.sheet_id not in sheet_map:
                    stock_sheet = (
                        self.session.query(StockSheet)
                        .filter(StockSheet.id == placement.sheet_id)
                        .first()
                    )
                    if not stock_sheet:
                        continue

                    task_sheet = TaskSheet(
                        task_id=task.id,
                        stock_sheet_id=placement.sheet_id,
                        sheet_index=len(sheet_map),
                        waste_mm2=0.0,
                    )
                    self.session.add(task_sheet)
                    self.session.flush()
                    sheet_map[placement.sheet_id] = task_sheet

                    movement = InventoryMovement(
                        stock_sheet_id=placement.sheet_id,
                        task_id=task.id,
                        delta=-1,
                        reason="cutting",
                        created_at=datetime.now(),
                    )
                    self.session.add(movement)
                    if stock_sheet.quantity > 0:
                        stock_sheet.quantity -= 1

                task_sheet = sheet_map.get(placement.sheet_id)
                if task_sheet:
                    self.session.add(
                        Placement(
                            task_sheet_id=task_sheet.id,
                            order_item_id=placement.piece_id,
                            x_mm=placement.x,
                            y_mm=placement.y,
                            width_mm=placement.width,
                            height_mm=placement.height,
                            rotated=placement.rotated,
                        )
                    )
                    self.session.add(
                        TaskOrderItemLink(task_id=task.id, order_item_id=placement.piece_id)
                    )

            task.kim_percent = result.kim_percent
            task.status = "done"
            task.completed_at = datetime.now()
            self.session.commit()

            self.progress_bar.setValue(100)
            self.status_label.setText(
                f"Готово. КИМ: {result.kim_percent:.2f}%, Время: {calc_time:.2f} сек"
            )
            self.btn_start.setEnabled(True)
            self._load_tasks()

            main_win = self.window()
            if hasattr(main_win, "tabs"):
                for i in range(main_win.tabs.count()):
                    tab = main_win.tabs.widget(i)
                    if hasattr(tab, "refresh_data"):
                        tab.refresh_data()

            result_tab_index = 5
            if hasattr(main_win, "tabs") and main_win.tabs.count() > result_tab_index:
                main_win.tabs.setCurrentIndex(result_tab_index)
                result_tab = main_win.tabs.widget(result_tab_index)
                if hasattr(result_tab, "task_combo"):
                    idx = result_tab.task_combo.findData(task.id)
                    if idx >= 0:
                        result_tab.task_combo.setCurrentIndex(idx)
                        if hasattr(result_tab, "_load_selected_task"):
                            result_tab._load_selected_task()
            main_win = self.window()
            if hasattr(main_win, "_update_status_bar"):
                main_win._update_status_bar()

            self._worker_thread.quit()

        def on_failed(error_text):
            self.btn_start.setEnabled(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Ошибка выполнения алгоритма")
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить раскрой:\n{error_text}")
            self._worker_thread.quit()

        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(on_finished)
        self._worker.failed.connect(on_failed)
        self._worker_thread.finished.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.start()

    def _view_result(self):
        row = self.results_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите задание")
            return
        main_win = self.window()
        if hasattr(main_win, "tabs"):
            main_win.tabs.setCurrentIndex(4)

    def _show_tasks_history(self):
        self._load_tasks()
