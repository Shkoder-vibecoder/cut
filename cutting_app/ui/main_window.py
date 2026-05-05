import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStatusBar, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from db.migrations import init_db
from db.session import get_session, close_session
from core.material_service import MaterialService
from core.stock_service import StockService
from core.order_service import OrderService
from core.job_service import JobService
from core.export_service import ExportService

from ui.views.materials_view import MaterialsView
from ui.views.stock_view import StockView
from ui.views.orders_view import OrdersView
from ui.views.templates_view import TemplatesView
from ui.views.job_view import JobView
from ui.views.result_view import ResultView

from config import AUTO_SAVE_INTERVAL


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ИС Раскрой - Информационная система оптимального раскроя листовых материалов")
        self.setGeometry(100, 100, 1200, 800)

        init_db()
        self.session = get_session()

        self.material_service = MaterialService(self.session)
        self.stock_service = StockService(self.session)
        self.order_service = OrderService(self.session)
        self.job_service = JobService(self.session)
        self.export_service = ExportService(self.session)

        self._setup_ui()
        self._setup_auto_save()

        self._update_status_bar()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        self.tabs.addTab(MaterialsView(self.material_service, self.session), "Материалы")
        self.tabs.addTab(StockView(self.stock_service, self.session), "Склад")
        self.tabs.addTab(OrdersView(self.order_service, self.session), "Заказы")
        self.tabs.addTab(TemplatesView(self.session), "Шаблоны")
        self.tabs.addTab(JobView(self.job_service, self.order_service, self.stock_service, self.session), "Задание раскроя")
        self.tabs.addTab(ResultView(self.job_service, self.export_service, self.session), "Результаты")

        main_layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")

    def _setup_auto_save(self):
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(AUTO_SAVE_INTERVAL * 1000)

    def _auto_save(self):
        try:
            self.session.commit()
            self.status_bar.showMessage("Автосохранение выполнено", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка автосохранения: {str(e)}", 3000)

    def _update_status_bar(self):
        try:
            stock = self.stock_service.get_current_stock()
            total_sheets = sum(s["quantity"] for s in stock.values())
            self.status_bar.showMessage(f"Склад: {total_sheets} листов | Готов к работе")
        except Exception:
            pass

    def closeEvent(self, event):
        try:
            self.session.commit()
        except Exception:
            pass
        close_session()
        event.accept()