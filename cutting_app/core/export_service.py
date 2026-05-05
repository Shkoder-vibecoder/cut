from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from PIL import Image
import io
import qrcode
import barcode
from barcode.writer import ImageWriter
import os


class ExportService:
    def __init__(self, session=None):
        self.session = session

    def export_to_pdf(self, task_sheets: list, output_path: str, task_info: dict = None):
        c = canvas.Canvas(output_path, pagesize=landscape(A4))
        width, height = landscape(A4)

        for idx, sheet in enumerate(task_sheets):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(20 * mm, height - 20 * mm, f"Карта раскроя - Лист {idx + 1}")

            if task_info:
                c.setFont("Helvetica", 10)
                c.drawString(20 * mm, height - 30 * mm, f"Заказ: {task_info.get('order_number', 'N/A')}")
                c.drawString(20 * mm, height - 37 * mm, f"КИМ: {task_info.get('kim_percent', 0):.2f}%")

            self._draw_sheet_content(c, sheet, 20 * mm, height - 50 * mm, width - 40 * mm, height - 80 * mm)

            if idx < len(task_sheets) - 1:
                c.showPage()

        c.save()

    def _draw_sheet_content(self, c: canvas.Canvas, sheet, x: float, y: float, w: float, h: float):
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(x, y, w, h)

        if hasattr(sheet, 'placements'):
            colors_list = [colors.red, colors.blue, colors.green, colors.orange, colors.purple, colors.cyan, colors.magenta, colors.yellow]
            for i, placement in enumerate(sheet.placements):
                scale_x = w / sheet.width if sheet.width > 0 else 1
                scale_y = h / sheet.height if sheet.height > 0 else 1
                scale = min(scale_x, scale_y)

                px = x + placement.x * scale
                py = y + placement.y * scale
                pw = placement.width * scale
                ph = placement.height * scale

                c.setFillColor(colors_list[i % len(colors_list)])
                c.rect(px, py, pw, ph, fill=1, stroke=1)

                c.setFillColor(colors.black)
                c.setFont("Helvetica", 6)
                name = getattr(placement, 'name', f'Деталь {i+1}')[:10]
                c.drawString(px + 2, py + ph / 2, name)

    def export_to_png(self, task_sheets: list, output_path: str, dpi: int = 150):
        """Экспорт карт раскроя в PNG формат"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            width_px = 800
            height_px = 600
            
            images = []
            for idx, sheet in enumerate(task_sheets):
                img = Image.new('RGB', (width_px, height_px), color=(245, 245, 245))
                draw = ImageDraw.Draw(img)
                
                # Масштабирование для отображения
                if hasattr(sheet, 'stock_sheet') and sheet.stock_sheet:
                    sheet_width = sheet.stock_sheet.format.width_mm if sheet.stock_sheet.format else 1000
                    sheet_height = sheet.stock_sheet.format.height_mm if sheet.stock_sheet.format else 800
                else:
                    sheet_width, sheet_height = 1000, 800
                
                scale_x = (width_px - 20) / sheet_width if sheet_width > 0 else 1
                scale_y = (height_px - 60) / sheet_height if sheet_height > 0 else 1
                scale = min(scale_x, scale_y)
                
                # Заголовок
                draw.text((10, 10), f"Лист {idx + 1}", fill=(0, 0, 0))
                
                # Границы листа
                draw.rectangle([
                    (10, 30),
                    (10 + sheet_width * scale, 30 + sheet_height * scale)
                ], outline=(100, 100, 100), width=2)
                
                # Размещения
                colors_list = [(255, 100, 100), (100, 100, 255), (100, 200, 100), 
                             (255, 150, 50), (200, 100, 200), (100, 200, 200)]
                
                if hasattr(sheet, 'placements'):
                    for i, placement in enumerate(sheet.placements):
                        x1 = 10 + placement.x_mm * scale
                        y1 = 30 + placement.y_mm * scale
                        x2 = x1 + placement.width_mm * scale
                        y2 = y1 + placement.height_mm * scale
                        
                        color = colors_list[i % len(colors_list)]
                        draw.rectangle([x1, y1, x2, y2], fill=color, outline=(0, 0, 0))
                        
                        # Текст
                        try:
                            piece_name = "Деталь"
                            draw.text((x1 + 2, y1 + 2), piece_name[:10], fill=(255, 255, 255))
                        except:
                            pass
                
                images.append(img)
            
            # Сохранение
            if images:
                if len(images) == 1:
                    images[0].save(output_path)
                else:
                    images[0].save(output_path, save_all=True, append_images=images[1:])
                return True
            return False
        except Exception as e:
            print(f"PNG export error: {e}")
            return False

    def generate_qr_code(self, data: str, output_path: str, box_size: int = 10, border: int = 2):
        qr = qrcode.QRCode(version=1, box_size=box_size, border=border)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)

    def generate_barcode(self, data: str, output_path: str):
        try:
            from barcode import Code128
            from barcode.writer import ImageWriter

            with open(output_path, 'wb') as f:
                Code128(data, writer=ImageWriter()).write(f)
        except Exception as e:
            print(f"Barcode generation error: {e}")

    def generate_label(self, piece_name: str, dimensions: str, order_number: str, output_path: str):
        from reportlab.lib.pagesizes import mm
        from reportlab.pdfgen import canvas as pdf_canvas

        label_w = 50 * mm
        label_h = 30 * mm

        c = pdf_canvas.Canvas(output_path, pagesize=(label_w, label_h))

        c.setFont("Helvetica-Bold", 12)
        c.drawString(5 * mm, label_h - 10 * mm, piece_name[:20])

        c.setFont("Helvetica", 10)
        c.drawString(5 * mm, label_h - 18 * mm, dimensions)

        c.setFont("Helvetica", 8)
        c.drawString(5 * mm, label_h - 26 * mm, order_number)

        qr_path = output_path.replace(".pdf", "_qr.png")
        self.generate_qr_code(f"{order_number}|{piece_name}|{dimensions}", qr_path)
        c.drawImage(qr_path, 35 * mm, 5 * mm, 12 * mm, 12 * mm)

        c.save()

    def get_summary(self, task) -> dict:
        summary = {
            "order_number": task.order_id,
            "kim_percent": task.kim_percent or 0,
            "total_sheets": len(task.task_sheets) if hasattr(task, 'task_sheets') else 0,
            "total_placements": 0,
            "total_waste_mm2": 0,
            "calculation_time": 0
        }

        if hasattr(task, 'task_sheets'):
            for ts in task.task_sheets:
                summary["total_placements"] += len(ts.placements)
                summary["total_waste_mm2"] += ts.waste_mm2 or 0

        return summary