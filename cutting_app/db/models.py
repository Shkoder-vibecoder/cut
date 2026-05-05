from sqlalchemy import create_engine, Integer, Float, String, Text, Boolean, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class MaterialType(Base):
    __tablename__ = "material_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    formats: Mapped[list["SheetFormat"]] = relationship(back_populates="material_type", cascade="all, delete-orphan")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="material_type", cascade="all, delete-orphan")


class SheetFormat(Base):
    __tablename__ = "sheet_format"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_type.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    height_mm: Mapped[float] = mapped_column(Float, nullable=False)
    thickness_mm: Mapped[float | None] = mapped_column(Float, nullable=True)

    material_type: Mapped["MaterialType"] = relationship(back_populates="formats")
    stock_sheets: Mapped[list["StockSheet"]] = relationship(back_populates="format")


class StockSheet(Base):
    __tablename__ = "stock_sheet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    format_id: Mapped[int] = mapped_column(Integer, ForeignKey("sheet_format.id"), nullable=False)
    texture: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    defects_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        CheckConstraint("texture IN ('none', 'horizontal', 'vertical')"),
        CheckConstraint("price >= 0"),
        CheckConstraint("quantity >= 0"),
    )

    format: Mapped["SheetFormat"] = relationship(back_populates="stock_sheets")
    movements: Mapped[list["InventoryMovement"]] = relationship(back_populates="stock_sheet")
    task_sheets: Mapped[list["TaskSheet"]] = relationship(back_populates="stock_sheet")


class Order(Base):
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(50), primary_key=True)
    client: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'in_progress', 'completed', 'archived')"),
    )

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    tasks: Mapped[list["CuttingTask"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(50), ForeignKey("orders.order_number"), nullable=False)
    material_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_type.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    height_mm: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    rotation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fibers: Mapped[str] = mapped_column(String(20), nullable=False, default="any")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("width_mm > 0"),
        CheckConstraint("height_mm > 0"),
        CheckConstraint("quantity > 0"),
        CheckConstraint("fibers IN ('any', 'horizontal', 'vertical')"),
    )

    order: Mapped["Order"] = relationship(back_populates="items")
    material_type: Mapped["MaterialType"] = relationship(back_populates="order_items")
    placements: Mapped[list["Placement"]] = relationship(back_populates="order_item")
    task_links: Mapped[list["TaskOrderItemLink"]] = relationship(back_populates="order_item")


class OrderTemplate(Base):
    __tablename__ = "order_template"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    positions_json: Mapped[list] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        CheckConstraint("positions_json IS NOT NULL"),
    )


class CuttingTask(Base):
    __tablename__ = "cutting_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(50), ForeignKey("orders.order_number"), nullable=False)
    cut_type: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    cut_width: Mapped[float] = mapped_column(Float, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(30), nullable=False)
    kim_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("cut_type IN ('guillotine', 'free')"),
        CheckConstraint("status IN ('pending', 'running', 'done', 'failed')"),
    )

    order: Mapped["Order"] = relationship(back_populates="tasks")
    task_sheets: Mapped[list["TaskSheet"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    item_links: Mapped[list["TaskOrderItemLink"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    movements: Mapped[list["InventoryMovement"]] = relationship(back_populates="task")


class TaskSheet(Base):
    __tablename__ = "task_sheet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("cutting_task.id"), nullable=False)
    stock_sheet_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_sheet.id"), nullable=False)
    sheet_index: Mapped[int] = mapped_column(Integer, nullable=False)
    waste_mm2: Mapped[float | None] = mapped_column(Float, nullable=True)

    task: Mapped["CuttingTask"] = relationship(back_populates="task_sheets")
    stock_sheet: Mapped["StockSheet"] = relationship(back_populates="task_sheets")
    placements: Mapped[list["Placement"]] = relationship(back_populates="task_sheet", cascade="all, delete-orphan")


class Placement(Base):
    __tablename__ = "placement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_sheet_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_sheet.id"), nullable=False)
    order_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("order_item.id"), nullable=False)
    x_mm: Mapped[float] = mapped_column(Float, nullable=False)
    y_mm: Mapped[float] = mapped_column(Float, nullable=False)
    width_mm: Mapped[float] = mapped_column(Float, nullable=False)
    height_mm: Mapped[float] = mapped_column(Float, nullable=False)
    rotated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    task_sheet: Mapped["TaskSheet"] = relationship(back_populates="placements")
    order_item: Mapped["OrderItem"] = relationship(back_populates="placements")


class TaskOrderItemLink(Base):
    __tablename__ = "task_order_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("cutting_task.id"), nullable=False)
    order_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("order_item.id"), nullable=False)

    task: Mapped["CuttingTask"] = relationship(back_populates="item_links")
    order_item: Mapped["OrderItem"] = relationship(back_populates="task_links")


class InventoryMovement(Base):
    __tablename__ = "inventory_movement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_sheet_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_sheet.id"), nullable=False)
    task_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cutting_task.id"), nullable=True)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        CheckConstraint("reason IN ('arrival', 'cutting', 'manual', 'return')"),
    )

    stock_sheet: Mapped["StockSheet"] = relationship(back_populates="movements")
    task: Mapped["CuttingTask"] = relationship(back_populates="movements")