from sqlalchemy.orm import Session
from db.models import StockSheet, InventoryMovement, SheetFormat
from typing import Optional
from datetime import datetime
import json


class StockService:
    def __init__(self, session: Session):
        self.session = session

    def add_stock_sheet(self, format_id: int, texture: str = "none", price: float = 0.0, quantity: int = 1, defects_json: list = None) -> Optional[StockSheet]:
        format = self.session.query(SheetFormat).filter(SheetFormat.id == format_id).first()
        if not format:
            return None

        defects = defects_json if defects_json is not None else []
        sheet = StockSheet(
            format_id=format_id,
            texture=texture,
            price=price,
            quantity=quantity,
            defects_json=defects
        )
        self.session.add(sheet)
        self.session.flush()

        movement = InventoryMovement(
            stock_sheet_id=sheet.id,
            delta=quantity,
            reason="arrival",
            created_at=datetime.now()
        )
        self.session.add(movement)
        self.session.commit()
        return sheet

    def get_stock_sheet(self, sheet_id: int) -> Optional[StockSheet]:
        return self.session.query(StockSheet).filter(StockSheet.id == sheet_id).first()

    def get_all_stock_sheets(self) -> list[StockSheet]:
        return self.session.query(StockSheet).all()

    def get_stock_by_format(self, format_id: int) -> list[StockSheet]:
        return self.session.query(StockSheet).filter(StockSheet.format_id == format_id).all()

    def update_stock_sheet(self, sheet_id: int, quantity: int = None, price: float = None, texture: str = None, defects_json: list = None) -> Optional[StockSheet]:
        sheet = self.get_stock_sheet(sheet_id)
        if sheet:
            if quantity is not None:
                sheet.quantity = quantity
            if price is not None:
                sheet.price = price
            if texture is not None:
                sheet.texture = texture
            if defects_json is not None:
                sheet.defects_json = defects_json
            self.session.commit()
        return sheet

    def delete_stock_sheet(self, sheet_id: int) -> bool:
        sheet = self.get_stock_sheet(sheet_id)
        if sheet:
            self.session.delete(sheet)
            self.session.commit()
            return True
        return False

    def adjust_quantity(self, sheet_id: int, delta: int, reason: str = "manual", task_id: int = None) -> Optional[StockSheet]:
        sheet = self.get_stock_sheet(sheet_id)
        if not sheet:
            return None

        new_quantity = sheet.quantity + delta
        if new_quantity < 0:
            return None

        sheet.quantity = new_quantity
        movement = InventoryMovement(
            stock_sheet_id=sheet_id,
            task_id=task_id,
            delta=delta,
            reason=reason,
            created_at=datetime.now()
        )
        self.session.add(movement)
        self.session.commit()
        return sheet

    def get_movements(self, sheet_id: int = None) -> list[InventoryMovement]:
        query = self.session.query(InventoryMovement)
        if sheet_id:
            query = query.filter(InventoryMovement.stock_sheet_id == sheet_id)
        return query.order_by(InventoryMovement.created_at.desc()).all()

    def get_current_stock(self) -> dict:
        sheets = self.get_all_stock_sheets()
        stock_by_format = {}
        for sheet in sheets:
            if sheet.format_id not in stock_by_format:
                stock_by_format[sheet.format_id] = {
                    "quantity": 0,
                    "price": sheet.price,
                    "texture": sheet.texture,
                    "format_name": sheet.format.name if sheet.format else "Unknown"
                }
            stock_by_format[sheet.format_id]["quantity"] += sheet.quantity
        return stock_by_format

    def backup_database(self, backup_path: str) -> bool:
        import shutil
        from config import get_database_path
        try:
            shutil.copy2(get_database_path(), backup_path)
            return True
        except Exception:
            return False

    def restore_database(self, backup_path: str) -> bool:
        import shutil
        from config import get_database_path
        try:
            shutil.copy2(backup_path, get_database_path())
            return True
        except Exception:
            return False
