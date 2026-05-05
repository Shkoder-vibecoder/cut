# Техническое описание API модулей

## `core.material_service.MaterialService`
- `create_material_type(name, description=None) -> MaterialType`
- `get_material_type(material_id) -> MaterialType | None`
- `get_all_material_types() -> list[MaterialType]`
- `update_material_type(material_id, name=None, description=None) -> MaterialType | None`
- `delete_material_type(material_id) -> bool`
- `create_sheet_format(material_type_id, name, width_mm, height_mm, thickness_mm=None) -> SheetFormat | None`
- `get_sheet_format(format_id) -> SheetFormat | None`
- `get_formats_by_material(material_type_id) -> list[SheetFormat]`
- `get_all_formats() -> list[SheetFormat]`
- `update_sheet_format(format_id, name=None, width_mm=None, height_mm=None, thickness_mm=None) -> SheetFormat | None`
- `delete_sheet_format(format_id) -> bool`

## `core.stock_service.StockService`
- `add_stock_sheet(format_id, texture="none", price=0.0, quantity=1, defects_json=None) -> StockSheet | None`
- `get_stock_sheet(sheet_id) -> StockSheet | None`
- `get_all_stock_sheets() -> list[StockSheet]`
- `get_stock_by_format(format_id) -> list[StockSheet]`
- `update_stock_sheet(sheet_id, quantity=None, price=None, texture=None, defects_json=None) -> StockSheet | None`
- `delete_stock_sheet(sheet_id) -> bool`
- `adjust_quantity(sheet_id, delta, reason="manual", task_id=None) -> StockSheet | None`
- `get_movements(sheet_id=None) -> list[InventoryMovement]`
- `get_current_stock() -> dict`
- `backup_database(backup_path) -> bool`
- `restore_database(backup_path) -> bool`

## `core.order_service.OrderService`
- `create_order(order_number, client=None) -> Order`
- `get_order(order_number) -> Order | None`
- `get_all_orders() -> list[Order]`
- `update_order(order_number, client=None, status=None) -> Order | None`
- `delete_order(order_number) -> bool`
- `add_order_item(order_number, material_type_id, name, width_mm, height_mm, quantity, rotation=True, fibers="any", priority=0) -> OrderItem | None`
- `get_order_item(item_id) -> OrderItem | None`
- `get_order_items(order_number) -> list[OrderItem]`
- `update_order_item(item_id, name=None, width_mm=None, height_mm=None, quantity=None, rotation=None, fibers=None, priority=None) -> OrderItem | None`
- `delete_order_item(item_id) -> bool`
- `import_items_from_dict(order_number, items_data) -> list[OrderItem]`

## `core.job_service.JobService`
- `create_task(order_id, cut_width, algorithm, cut_type="free") -> CuttingTask | None`
- `get_task(task_id) -> CuttingTask | None`
- `get_all_tasks() -> list[CuttingTask]`
- `get_tasks_by_order(order_id) -> list[CuttingTask]`
- `update_task_status(task_id, status, kim_percent=None) -> CuttingTask | None`
- `run_task_async(task_id, sheets, pieces, params, progress_callback=None) -> None`
- `get_task_sheets(task_id) -> list[TaskSheet]`
- `get_task_placements(task_id) -> list[Placement]`
- `delete_task(task_id) -> bool`

## `core.export_service.ExportService`
- `export_to_pdf(task_sheets, output_path, task_info=None) -> bool`
- `export_to_png(task_sheets, output_path, dpi=150) -> bool`
- `generate_qr_code(data, output_path, box_size=10, border=2) -> bool`
- `generate_barcode(data, output_path) -> bool`
- `generate_label(piece_name, dimensions, order_number, output_path) -> bool`
- `get_summary(task) -> dict`

## Алгоритмы (`algorithms`)
- `GreedyAlgorithm.solve(sheets, pieces, params) -> CuttingResult`
- `GeneticAlgorithm.solve(sheets, pieces, params) -> CuttingResult`
- `AnnealingAlgorithm.solve(sheets, pieces, params) -> CuttingResult`
