import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.migrations import init_db, reset_db
from db.session import get_session, close_session
from core.material_service import MaterialService
from core.stock_service import StockService
from core.order_service import OrderService
from PIL import Image, ImageDraw


def _ensure_seed_image() -> str:
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    image_path = os.path.join(assets_dir, "seed_sheet_preview.png")

    if not os.path.exists(image_path):
        img = Image.new("RGB", (1200, 800), color=(243, 243, 236))
        draw = ImageDraw.Draw(img)
        draw.rectangle((80, 80, 1120, 720), outline=(70, 70, 70), width=4)
        draw.rectangle((120, 120, 520, 360), fill=(122, 180, 255), outline=(20, 20, 20), width=2)
        draw.rectangle((560, 120, 980, 320), fill=(255, 171, 145), outline=(20, 20, 20), width=2)
        draw.rectangle((120, 400, 420, 680), fill=(168, 223, 168), outline=(20, 20, 20), width=2)
        draw.rectangle((460, 360, 980, 680), fill=(238, 206, 132), outline=(20, 20, 20), width=2)
        draw.text((90, 30), "Seed preview: cutting map", fill=(35, 35, 35))
        img.save(image_path)

    return image_path


def seed_data(reset: bool = False):
    if reset:
        reset_db()
    else:
        init_db()

    session = get_session()

    material_service = MaterialService(session)
    stock_service = StockService(session)
    order_service = OrderService(session)

    image_path = _ensure_seed_image()

    print("Creating materials...")
    m1 = material_service.create_material_type("ЛДСП", "Ламинированная древесно-стружечная плита")
    m2 = material_service.create_material_type("МДФ", "Мелкодисперсная фракция")
    m3 = material_service.create_material_type("Фанера", "Березовая фанера")

    print("Creating sheet formats...")
    f1 = material_service.create_sheet_format(m1.id, "ЛДСП 2800x2070", 2800, 2070, 16)
    f2 = material_service.create_sheet_format(m1.id, "ЛДСП 2500x1830", 2500, 1830, 16)
    f3 = material_service.create_sheet_format(m2.id, "МДФ 2800x2070", 2800, 2070, 18)
    f4 = material_service.create_sheet_format(m3.id, "Фанера 1525x1525", 1525, 1525, 12)

    print("Adding stock sheets...")
    stock_service.add_stock_sheet(
        f1.id,
        "horizontal",
        1500.0,
        15,
        defects_json=[
            {
                "type": "preview_image",
                "path": image_path,
                "note": "Тестовое изображение листа для демонстрации данных склада",
            }
        ],
    )
    stock_service.add_stock_sheet(f1.id, "horizontal", 1500.0, 12)
    stock_service.add_stock_sheet(f2.id, "vertical", 1200.0, 20)
    stock_service.add_stock_sheet(
        f3.id,
        "none",
        2100.0,
        8,
        defects_json=[
            {
                "x": 420,
                "y": 350,
                "w": 120,
                "h": 75,
                "severity": "minor",
            }
        ],
    )
    stock_service.add_stock_sheet(
        f4.id,
        "none",
        800.0,
        25,
        defects_json=[
            {
                "type": "preview_image",
                "path": image_path,
            }
        ],
    )

    print("Creating orders...")
    order1 = order_service.create_order("ORD-2025-001", "Мебельная фабрика 'Комфорт'")
    order2 = order_service.create_order("ORD-2025-002", "ООО 'СтройИнтерьер'")

    print("Adding order items...")
    order_service.add_order_item(order1.order_number, m1.id, "Фасад шкафа верхний", 600, 400, 4, True, "any", 1)
    order_service.add_order_item(order1.order_number, m1.id, "Фасад шкафа нижний", 600, 600, 4, True, "any", 1)
    order_service.add_order_item(order1.order_number, m1.id, "Боковина левая", 400, 2000, 8, False, "any", 2)
    order_service.add_order_item(order1.order_number, m1.id, "Боковина правая", 400, 2000, 8, False, "any", 2)
    order_service.add_order_item(order1.order_number, m1.id, "Крыша стола", 1200, 600, 2, True, "horizontal", 3)
    order_service.add_order_item(order1.order_number, m1.id, "Полка", 500, 400, 12, True, "any", 0)

    order_service.add_order_item(order2.order_number, m3.id, "Стенка задняя", 800, 600, 6, True, "any", 1)
    order_service.add_order_item(order2.order_number, m3.id, "Дверь", 450, 900, 4, True, "any", 2)
    order_service.add_order_item(order2.order_number, m3.id, "Ящик", 400, 300, 16, True, "any", 0)

    session.commit()
    close_session()

    print(f"Test data seeded successfully! Image: {image_path}")

if __name__ == "__main__":
    seed_data(reset="--reset" in sys.argv)
