from sqlalchemy.orm import Session
from db.models import CuttingTask, TaskSheet, Placement, OrderItem, StockSheet, TaskOrderItemLink, InventoryMovement
from algorithms.base import CuttingParams, Sheet, Piece, CuttingResult
from algorithms.greedy import GreedyAlgorithm
from algorithms.genetic import GeneticAlgorithm
from algorithms.annealing import AnnealingAlgorithm
from typing import Optional
from datetime import datetime
import threading
import time


class JobService:
    def __init__(self, session: Session):
        self.session = session
        self._active_tasks = {}
        self._task_lock = threading.Lock()

    def create_task(self, order_id: str, cut_width: float, algorithm: str, cut_type: str = "free") -> Optional[CuttingTask]:
        task = CuttingTask(
            order_id=order_id,
            cut_type=cut_type,
            cut_width=cut_width,
            algorithm=algorithm,
            status="pending",
            created_at=datetime.now()
        )
        self.session.add(task)
        self.session.commit()
        return task

    def get_task(self, task_id: int) -> Optional[CuttingTask]:
        return self.session.query(CuttingTask).filter(CuttingTask.id == task_id).first()

    def get_all_tasks(self) -> list[CuttingTask]:
        return self.session.query(CuttingTask).all()

    def get_tasks_by_order(self, order_id: str) -> list[CuttingTask]:
        return self.session.query(CuttingTask).filter(CuttingTask.order_id == order_id).all()

    def update_task_status(self, task_id: int, status: str, kim_percent: float = None) -> Optional[CuttingTask]:
        task = self.get_task(task_id)
        if task:
            task.status = status
            if kim_percent is not None:
                task.kim_percent = kim_percent
            if status in ("done", "failed"):
                task.completed_at = datetime.now()
            self.session.commit()
        return task

    def run_task_async(self, task_id: int, sheets: list, pieces: list, params: CuttingParams, progress_callback=None):
        def worker():
            with self._task_lock:
                self._active_tasks[task_id] = {"status": "running", "progress": 0}

            task = self.get_task(task_id)
            if not task:
                return

            self.update_task_status(task_id, "running")

            if params.algorithm == "greedy":
                algo = GreedyAlgorithm()
            elif params.algorithm == "genetic":
                algo = GeneticAlgorithm()
            elif params.algorithm == "annealing":
                algo = AnnealingAlgorithm()
            else:
                algo = GreedyAlgorithm()

            result = algo.solve(sheets, pieces, params)

            self._save_result(task_id, result)

            with self._task_lock:
                self._active_tasks[task_id] = {"status": result.status, "progress": 100}

            if progress_callback:
                progress_callback(100, result)

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

    def _save_result(self, task_id: int, result: CuttingResult):
        task = self.get_task(task_id)
        if not task:
            return

        task.kim_percent = result.kim_percent
        task.status = result.status
        task.completed_at = datetime.now()

        sheet_map = {}
        for placement in result.placements:
            if placement.sheet_id not in sheet_map:
                stock_sheet = self.session.query(StockSheet).filter(StockSheet.id == placement.sheet_id).first()
                if not stock_sheet:
                    continue

                task_sheet = TaskSheet(
                    task_id=task_id,
                    stock_sheet_id=placement.sheet_id,
                    sheet_index=len(sheet_map),
                    waste_mm2=0.0
                )
                self.session.add(task_sheet)
                self.session.flush()
                sheet_map[placement.sheet_id] = task_sheet

            task_sheet = sheet_map[placement.sheet_id]

            placement_obj = Placement(
                task_sheet_id=task_sheet.id,
                order_item_id=placement.piece_id,
                x_mm=placement.x,
                y_mm=placement.y,
                width_mm=placement.width,
                height_mm=placement.height,
                rotated=placement.rotated
            )
            self.session.add(placement_obj)

            item_link = TaskOrderItemLink(
                task_id=task_id,
                order_item_id=placement.piece_id
            )
            self.session.add(item_link)

        self.session.commit()

        self._write_off_sheets(task_id, list(sheet_map.keys()))

    def _write_off_sheets(self, task_id: int, stock_sheet_ids: list):
        for stock_sheet_id in stock_sheet_ids:
            movement = InventoryMovement(
                stock_sheet_id=stock_sheet_id,
                task_id=task_id,
                delta=-1,
                reason="cutting",
                created_at=datetime.now()
            )
            self.session.add(movement)

            stock_sheet = self.session.query(StockSheet).filter(StockSheet.id == stock_sheet_id).first()
            if stock_sheet and stock_sheet.quantity > 0:
                stock_sheet.quantity -= 1

        self.session.commit()

    def get_task_sheets(self, task_id: int) -> list[TaskSheet]:
        return self.session.query(TaskSheet).filter(TaskSheet.task_id == task_id).all()

    def get_task_placements(self, task_id: int) -> list[Placement]:
        task_sheets = self.get_task_sheets(task_id)
        placements = []
        for ts in task_sheets:
            placements.extend(self.session.query(Placement).filter(Placement.task_sheet_id == ts.id).all())
        return placements

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        return False
