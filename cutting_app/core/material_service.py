from sqlalchemy.orm import Session
from db.models import MaterialType, SheetFormat
from typing import Optional


class MaterialService:
    def __init__(self, session: Session):
        self.session = session

    def create_material_type(self, name: str, description: str = None) -> MaterialType:
        material = MaterialType(name=name, description=description)
        self.session.add(material)
        self.session.commit()
        return material

    def get_material_type(self, material_id: int) -> Optional[MaterialType]:
        return self.session.query(MaterialType).filter(MaterialType.id == material_id).first()

    def get_all_material_types(self) -> list[MaterialType]:
        return self.session.query(MaterialType).all()

    def update_material_type(self, material_id: int, name: str = None, description: str = None) -> Optional[MaterialType]:
        material = self.get_material_type(material_id)
        if material:
            if name is not None:
                material.name = name
            if description is not None:
                material.description = description
            self.session.commit()
        return material

    def delete_material_type(self, material_id: int) -> bool:
        material = self.get_material_type(material_id)
        if material:
            self.session.delete(material)
            self.session.commit()
            return True
        return False

    def create_sheet_format(self, material_type_id: int, name: str, width_mm: float, height_mm: float, thickness_mm: float = None) -> Optional[SheetFormat]:
        material = self.get_material_type(material_type_id)
        if not material:
            return None
        format = SheetFormat(
            material_type_id=material_type_id,
            name=name,
            width_mm=width_mm,
            height_mm=height_mm,
            thickness_mm=thickness_mm
        )
        self.session.add(format)
        self.session.commit()
        return format

    def get_sheet_format(self, format_id: int) -> Optional[SheetFormat]:
        return self.session.query(SheetFormat).filter(SheetFormat.id == format_id).first()

    def get_formats_by_material(self, material_type_id: int) -> list[SheetFormat]:
        return self.session.query(SheetFormat).filter(SheetFormat.material_type_id == material_type_id).all()

    def get_all_formats(self) -> list[SheetFormat]:
        return self.session.query(SheetFormat).all()

    def update_sheet_format(self, format_id: int, name: str = None, width_mm: float = None, height_mm: float = None, thickness_mm: float = None) -> Optional[SheetFormat]:
        format = self.get_sheet_format(format_id)
        if format:
            if name is not None:
                format.name = name
            if width_mm is not None:
                format.width_mm = width_mm
            if height_mm is not None:
                format.height_mm = height_mm
            if thickness_mm is not None:
                format.thickness_mm = thickness_mm
            self.session.commit()
        return format

    def delete_sheet_format(self, format_id: int) -> bool:
        format = self.get_sheet_format(format_id)
        if format:
            self.session.delete(format)
            self.session.commit()
            return True
        return False