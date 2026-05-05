# Структура базы данных

Ниже описана актуальная схема SQLite, реализованная в `db/models.py`.

## `material_type`
- `id` INTEGER PK AUTOINCREMENT
- `name` VARCHAR(100) UNIQUE NOT NULL
- `description` TEXT NULL

## `sheet_format`
- `id` INTEGER PK AUTOINCREMENT
- `material_type_id` INTEGER FK -> `material_type.id` NOT NULL
- `name` VARCHAR(100) NOT NULL
- `width_mm` FLOAT NOT NULL
- `height_mm` FLOAT NOT NULL
- `thickness_mm` FLOAT NULL

## `stock_sheet`
- `id` INTEGER PK AUTOINCREMENT
- `format_id` INTEGER FK -> `sheet_format.id` NOT NULL
- `texture` VARCHAR(20) CHECK IN (`none`, `horizontal`, `vertical`)
- `price` FLOAT CHECK `price >= 0`
- `quantity` INTEGER CHECK `quantity >= 0`
- `defects_json` JSON NOT NULL
- `created_at` DATETIME NOT NULL

## `orders`
- `order_number` VARCHAR(50) PK
- `client` VARCHAR(200) NULL
- `status` VARCHAR(20) CHECK IN (`draft`, `in_progress`, `completed`, `archived`)
- `created_at` DATETIME NOT NULL
- `updated_at` DATETIME NOT NULL

## `order_item`
- `id` INTEGER PK AUTOINCREMENT
- `order_id` VARCHAR(50) FK -> `orders.order_number` NOT NULL
- `material_type_id` INTEGER FK -> `material_type.id` NOT NULL
- `name` VARCHAR(200) NOT NULL
- `width_mm` FLOAT CHECK `width_mm > 0`
- `height_mm` FLOAT CHECK `height_mm > 0`
- `quantity` INTEGER CHECK `quantity > 0`
- `rotation` BOOLEAN NOT NULL
- `fibers` VARCHAR(20) CHECK IN (`any`, `horizontal`, `vertical`)
- `priority` INTEGER NOT NULL

## `order_template`
- `id` INTEGER PK AUTOINCREMENT
- `name` VARCHAR(200) UNIQUE NOT NULL
- `positions_json` JSON NOT NULL

## `cutting_task`
- `id` INTEGER PK AUTOINCREMENT
- `order_id` VARCHAR(50) FK -> `orders.order_number` NOT NULL
- `cut_type` VARCHAR(20) CHECK IN (`guillotine`, `free`)
- `cut_width` FLOAT NOT NULL
- `algorithm` VARCHAR(30) NOT NULL
- `kim_percent` FLOAT NULL
- `status` VARCHAR(20) CHECK IN (`pending`, `running`, `done`, `failed`)
- `created_at` DATETIME NOT NULL
- `completed_at` DATETIME NULL

## `task_sheet`
- `id` INTEGER PK AUTOINCREMENT
- `task_id` INTEGER FK -> `cutting_task.id` NOT NULL
- `stock_sheet_id` INTEGER FK -> `stock_sheet.id` NOT NULL
- `sheet_index` INTEGER NOT NULL
- `waste_mm2` FLOAT NULL

## `placement`
- `id` INTEGER PK AUTOINCREMENT
- `task_sheet_id` INTEGER FK -> `task_sheet.id` NOT NULL
- `order_item_id` INTEGER FK -> `order_item.id` NOT NULL
- `x_mm` FLOAT NOT NULL
- `y_mm` FLOAT NOT NULL
- `width_mm` FLOAT NOT NULL
- `height_mm` FLOAT NOT NULL
- `rotated` BOOLEAN NOT NULL

## `task_order_item`
- `id` INTEGER PK AUTOINCREMENT
- `task_id` INTEGER FK -> `cutting_task.id` NOT NULL
- `order_item_id` INTEGER FK -> `order_item.id` NOT NULL

## `inventory_movement`
- `id` INTEGER PK AUTOINCREMENT
- `stock_sheet_id` INTEGER FK -> `stock_sheet.id` NOT NULL
- `task_id` INTEGER FK -> `cutting_task.id` NULL
- `delta` INTEGER NOT NULL
- `reason` VARCHAR(30) CHECK IN (`arrival`, `cutting`, `manual`, `return`)
- `created_at` DATETIME NOT NULL
