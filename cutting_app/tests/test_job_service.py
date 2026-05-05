import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.base import CuttingResult, PlacementResult
from core.job_service import JobService
from core.material_service import MaterialService
from core.order_service import OrderService
from core.stock_service import StockService
from db.migrations import reset_db
from db.session import close_session, get_session, reset_engine


@pytest.fixture
def session(tmp_path):
    os.environ["CUTTING_DB_PATH"] = str(tmp_path / "job_service.db")
    reset_engine()
    reset_db()
    session = get_session()
    yield session
    close_session()
    reset_engine()


def test_job_service_save_result_and_writeoff(session):
    material_service = MaterialService(session)
    stock_service = StockService(session)
    order_service = OrderService(session)
    job_service = JobService(session)

    mat = material_service.create_material_type("JobMat", "desc")
    fmt = material_service.create_sheet_format(mat.id, "Fmt", 1000, 1000, 16)
    stock = stock_service.add_stock_sheet(fmt.id, "none", 500.0, 3)
    order = order_service.create_order("ORD-JOB-1", "Client")
    item = order_service.add_order_item(order.order_number, mat.id, "Part", 200, 200, 1)

    task = job_service.create_task(order.order_number, 3.0, "greedy", "free")

    result = CuttingResult(
        placements=[
            PlacementResult(
                piece_id=item.id,
                sheet_id=stock.id,
                x=10.0,
                y=10.0,
                width=200.0,
                height=200.0,
                rotated=False,
            )
        ],
        kim_percent=85.0,
        total_sheets_used=1,
        status="done",
    )

    job_service._save_result(task.id, result)

    saved = job_service.get_task(task.id)
    assert saved is not None
    assert saved.status == "done"
    assert saved.kim_percent == 85.0

    placements = job_service.get_task_placements(task.id)
    assert len(placements) == 1

    updated_stock = stock_service.get_stock_sheet(stock.id)
    assert updated_stock.quantity == 2


def test_job_service_update_and_delete(session):
    order_service = OrderService(session)
    material_service = MaterialService(session)
    stock_service = StockService(session)
    job_service = JobService(session)

    mat = material_service.create_material_type("Mat2", "desc")
    fmt = material_service.create_sheet_format(mat.id, "Fmt2", 800, 600, 16)
    stock_service.add_stock_sheet(fmt.id, "none", 200.0, 1)
    order = order_service.create_order("ORD-JOB-2", "Client")

    task = job_service.create_task(order.order_number, 2.0, "greedy", "free")
    assert job_service.update_task_status(task.id, "running") is not None
    assert job_service.delete_task(task.id) is True
