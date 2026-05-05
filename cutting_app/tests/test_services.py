import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.migrations import reset_db
from db.session import get_session, close_session, reset_engine
from core.stock_service import StockService
from core.order_service import OrderService
from core.material_service import MaterialService
from core.export_service import ExportService
from datetime import datetime


@pytest.fixture
def session(tmp_path):
    os.environ["CUTTING_DB_PATH"] = str(tmp_path / "test.db")
    reset_engine()
    reset_db()
    session = get_session()
    yield session
    close_session()
    reset_engine()


class TestStockService:
    def test_add_stock_sheet(self, session):
        stock_service = StockService(session)

        material_service = MaterialService(session)
        mat = material_service.create_material_type("Test Material", "Test description")
        format_obj = material_service.create_sheet_format(mat.id, "Test Format", 1000, 2000, 16)

        sheet = stock_service.add_stock_sheet(format_obj.id, "none", 1000.0, 10)
        assert sheet is not None
        assert sheet.quantity == 10
        assert sheet.price == 1000.0

    def test_adjust_quantity(self, session):
        stock_service = StockService(session)

        material_service = MaterialService(session)
        mat = material_service.create_material_type("Test Material 2", "Test")
        format_obj = material_service.create_sheet_format(mat.id, "Format 2", 1000, 2000, 16)

        sheet = stock_service.add_stock_sheet(format_obj.id, "none", 500.0, 5)
        assert sheet.quantity == 5

        result = stock_service.adjust_quantity(sheet.id, -2, "manual")
        assert result.quantity == 3

    def test_get_movements(self, session):
        stock_service = StockService(session)

        material_service = MaterialService(session)
        mat = material_service.create_material_type("Material 3", "Desc")
        format_obj = material_service.create_sheet_format(mat.id, "Format 3", 1500, 2500, 18)

        sheet = stock_service.add_stock_sheet(format_obj.id, "horizontal", 800.0, 8)
        stock_service.adjust_quantity(sheet.id, -1, "cutting")

        movements = stock_service.get_movements(sheet.id)
        assert len(movements) >= 1


class TestOrderService:
    def test_create_order(self, session):
        order_service = OrderService(session)

        order = order_service.create_order("ORD-TEST-001", "Test Client")
        assert order is not None
        assert order.order_number == "ORD-TEST-001"
        assert order.status == "draft"

    def test_add_order_item(self, session):
        order_service = OrderService(session)
        material_service = MaterialService(session)

        mat = material_service.create_material_type("Material 4", "Desc")
        order = order_service.create_order("ORD-TEST-002", "Client 2")

        item = order_service.add_order_item(
            order.order_number, mat.id,
            "Test Part", 500, 300, 4, True, "any", 1
        )
        assert item is not None
        assert item.name == "Test Part"
        assert item.width_mm == 500

    def test_get_order_items(self, session):
        order_service = OrderService(session)
        material_service = MaterialService(session)

        mat = material_service.create_material_type("Material 5", "Desc")
        order = order_service.create_order("ORD-TEST-003", "Client 3")

        order_service.add_order_item(order.order_number, mat.id, "Part 1", 100, 100, 2, True, "any", 0)
        order_service.add_order_item(order.order_number, mat.id, "Part 2", 200, 200, 3, True, "any", 0)

        items = order_service.get_order_items(order.order_number)
        assert len(items) == 2

    def test_delete_order(self, session):
        order_service = OrderService(session)
        order = order_service.create_order("ORD-TEST-004", "Client 4")

        result = order_service.delete_order("ORD-TEST-004")
        assert result is True

        deleted = order_service.get_order("ORD-TEST-004")
        assert deleted is None


class TestMaterialService:
    def test_create_material_type(self, session):
        material_service = MaterialService(session)

        mat = material_service.create_material_type("New Material", "Description")
        assert mat is not None
        assert mat.name == "New Material"

    def test_create_sheet_format(self, session):
        material_service = MaterialService(session)
        mat = material_service.create_material_type("Mat for Format", "Desc")

        fmt = material_service.create_sheet_format(mat.id, "Big Sheet", 3000, 2500, 18)
        assert fmt is not None
        assert fmt.width_mm == 3000
        assert fmt.height_mm == 2500

    def test_cascade_delete(self, session):
        material_service = MaterialService(session)

        mat = material_service.create_material_type("Mat for Cascade", "Will be deleted")
        fmt = material_service.create_sheet_format(mat.id, "Cascade Format", 2000, 1000, 16)

        from db.models import OrderItem, Order
        order = Order(order_number="ORD-CASCADE-001", status="draft")
        session.add(order)
        session.flush()

        item = OrderItem(
            order_id=order.order_number,
            material_type_id=mat.id,
            name="Cascade Part",
            width_mm=100, height_mm=100, quantity=1
        )
        session.add(item)
        session.commit()

        material_service.delete_material_type(mat.id)

        remaining_items = session.query(OrderItem).filter(OrderItem.material_type_id == mat.id).all()
        assert len(remaining_items) == 0


class TestExportService:
    def test_generate_label_with_qr_and_barcode(self, session, tmp_path):
        export_service = ExportService(session)
        output = tmp_path / "label.pdf"
        export_service.generate_label("Part A", "100x200", "ORD-1", str(output))

        assert output.exists()
        assert (tmp_path / "label_qr.png").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
