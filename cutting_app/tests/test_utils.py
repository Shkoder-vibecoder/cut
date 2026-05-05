import csv
import os
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.importer import Importer
from utils.validators import (
    validate_cut_params,
    validate_dimensions,
    validate_order_number,
    validate_price,
    validate_quantity,
)


def test_validate_dimensions_ok():
    ok, msg = validate_dimensions(100, 200)
    assert ok is True
    assert msg == ""


def test_validate_dimensions_invalid():
    ok, _ = validate_dimensions(-1, 100)
    assert ok is False


def test_validate_quantity_and_price_and_order():
    assert validate_quantity(2)[0] is True
    assert validate_quantity(0)[0] is False
    assert validate_price(10.5)[0] is True
    assert validate_price(-1)[0] is False
    assert validate_order_number("ORD-1")[0] is True
    assert validate_order_number(" ")[0] is False


def test_validate_cut_params():
    assert validate_cut_params(3.0, 10.0, 2800, 2070)[0] is True
    assert validate_cut_params(-1.0, 10.0, 2800, 2070)[0] is False


def test_import_csv(tmp_path):
    csv_path = tmp_path / "items.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "width", "height", "quantity", "rotation", "fibers", "material_type_id"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "name": "Деталь А",
                "width": "500",
                "height": "300",
                "quantity": "2",
                "rotation": "true",
                "fibers": "any",
                "material_type_id": "1",
            }
        )

    data = Importer().import_csv(str(csv_path))
    assert len(data) == 1
    assert data[0]["name"] == "Деталь А"
    assert data[0]["width_mm"] == 500.0


def test_import_excel(tmp_path):
    xlsx_path = tmp_path / "items.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["name", "width", "height", "quantity"])
    ws.append(["Деталь Б", 700, 450, 3])
    wb.save(xlsx_path)

    data = Importer().import_excel(str(xlsx_path))
    assert len(data) == 1
    assert data[0]["name"] == "Деталь Б"
    assert data[0]["quantity"] == 3
