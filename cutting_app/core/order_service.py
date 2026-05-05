from sqlalchemy.orm import Session
from db.models import Order, OrderItem, MaterialType
from typing import Optional
from datetime import datetime
import json


class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def create_order(self, order_number: str, client: str = None) -> Order:
        order = Order(
            order_number=order_number,
            client=client,
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.session.add(order)
        self.session.commit()
        return order

    def get_order(self, order_number: str) -> Optional[Order]:
        return self.session.query(Order).filter(Order.order_number == order_number).first()

    def get_all_orders(self) -> list[Order]:
        return self.session.query(Order).all()

    def update_order(self, order_number: str, client: str = None, status: str = None) -> Optional[Order]:
        order = self.get_order(order_number)
        if order:
            if client is not None:
                order.client = client
            if status is not None:
                order.status = status
            order.updated_at = datetime.now()
            self.session.commit()
        return order

    def delete_order(self, order_number: str) -> bool:
        order = self.get_order(order_number)
        if order:
            self.session.delete(order)
            self.session.commit()
            return True
        return False

    def add_order_item(self, order_number: str, material_type_id: int, name: str, width_mm: float, height_mm: float, quantity: int, rotation: bool = True, fibers: str = "any", priority: int = 0) -> Optional[OrderItem]:
        order = self.get_order(order_number)
        if not order:
            return None

        item = OrderItem(
            order_id=order_number,
            material_type_id=material_type_id,
            name=name,
            width_mm=width_mm,
            height_mm=height_mm,
            quantity=quantity,
            rotation=rotation,
            fibers=fibers,
            priority=priority
        )
        self.session.add(item)
        self.session.commit()
        return item

    def get_order_item(self, item_id: int) -> Optional[OrderItem]:
        return self.session.query(OrderItem).filter(OrderItem.id == item_id).first()

    def get_order_items(self, order_number: str) -> list[OrderItem]:
        return self.session.query(OrderItem).filter(OrderItem.order_id == order_number).all()

    def update_order_item(self, item_id: int, name: str = None, width_mm: float = None, height_mm: float = None, quantity: int = None, rotation: bool = None, fibers: str = None, priority: int = None) -> Optional[OrderItem]:
        item = self.get_order_item(item_id)
        if item:
            if name is not None:
                item.name = name
            if width_mm is not None:
                item.width_mm = width_mm
            if height_mm is not None:
                item.height_mm = height_mm
            if quantity is not None:
                item.quantity = quantity
            if rotation is not None:
                item.rotation = rotation
            if fibers is not None:
                item.fibers = fibers
            if priority is not None:
                item.priority = priority
            self.session.commit()
        return item

    def delete_order_item(self, item_id: int) -> bool:
        item = self.get_order_item(item_id)
        if item:
            self.session.delete(item)
            self.session.commit()
            return True
        return False

    def import_items_from_dict(self, order_number: str, items_data: list[dict]) -> list[OrderItem]:
        order = self.get_order(order_number)
        if not order:
            return []

        created_items = []
        for item_data in items_data:
            item = OrderItem(
                order_id=order_number,
                material_type_id=item_data.get("material_type_id", 1),
                name=item_data.get("name", "Unknown"),
                width_mm=item_data.get("width_mm", 0),
                height_mm=item_data.get("height_mm", 0),
                quantity=item_data.get("quantity", 1),
                rotation=item_data.get("rotation", True),
                fibers=item_data.get("fibers", "any"),
                priority=item_data.get("priority", 0)
            )
            self.session.add(item)
            created_items.append(item)

        self.session.commit()
        return created_items