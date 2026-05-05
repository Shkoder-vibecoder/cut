import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.export_service import ExportService


class DummyPlacement:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.x_mm = x
        self.y_mm = y
        self.width_mm = w
        self.height_mm = h
        self.name = "Part"


class DummySheet:
    def __init__(self):
        self.width = 1000
        self.height = 800
        self.placements = [DummyPlacement(10, 10, 200, 100)]


def test_export_pdf_and_png_and_summary(tmp_path):
    service = ExportService()
    sheet = DummySheet()

    pdf_path = tmp_path / "cut_map.pdf"
    png_path = tmp_path / "cut_map.png"

    service.export_to_pdf([sheet], str(pdf_path), {"order_number": "ORD-X", "kim_percent": 88.8})
    assert pdf_path.exists()

    assert service.export_to_png([sheet], str(png_path)) is True
    assert png_path.exists()

    class DummyTask:
        order_id = "ORD-X"
        kim_percent = 88.8
        task_sheets = []

    summary = service.get_summary(DummyTask())
    assert summary["order_number"] == "ORD-X"
    assert summary["kim_percent"] == 88.8
