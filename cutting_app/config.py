import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# База данных
DEFAULT_DATABASE_PATH = os.path.join(BASE_DIR, "cutting_app.db")
DATABASE_ENV_VAR = "CUTTING_DB_PATH"

def get_database_path() -> str:
    return os.getenv(DATABASE_ENV_VAR, DEFAULT_DATABASE_PATH)

# Технологические параметры раскроя
DEFAULT_CUT_WIDTH = 3.0
DEFAULT_EDGE_OFFSET = 0.0          # исправлено: было 10.0
DEFAULT_GUILLOTINE_DEPTH = float("inf")

# Генетический алгоритм
GA_POPULATION_SIZE = 50
GA_GENERATIONS = 500
GA_MUTATION_RATE = 0.05
GA_CROSSOVER_RATE = 0.85
GA_TOURNAMENT_K = 3

# Имитация отжига
SA_INITIAL_TEMP = 1000.0
SA_COOLING_RATE = 0.995
SA_MIN_TEMP = 1.0

# Система
AUTO_SAVE_INTERVAL = 300
MAX_CUTTING_TIME_SECONDS = 60
MAX_CUTTING_PIECES = 200

# Экспорт и импорт
DEFAULT_EXPORT_DIR = os.path.join(BASE_DIR, "exports")
SUPPORTED_IMPORT_FORMATS = (".csv", ".xlsx")

# Интерфейс / визуализация
DEFAULT_ZOOM_STEP = 0.1
MIN_ZOOM = 0.1
MAX_ZOOM = 5.0


def _validate_config() -> None:
    if not isinstance(GA_POPULATION_SIZE, int) or GA_POPULATION_SIZE <= 0:
        raise ValueError("GA_POPULATION_SIZE must be positive int")
    if not isinstance(GA_GENERATIONS, int) or GA_GENERATIONS <= 0:
        raise ValueError("GA_GENERATIONS must be positive int")
    if not (0.0 < GA_MUTATION_RATE < 1.0):
        raise ValueError("GA_MUTATION_RATE must be in (0, 1)")
    if not (0.0 < GA_CROSSOVER_RATE < 1.0):
        raise ValueError("GA_CROSSOVER_RATE must be in (0, 1)")


_validate_config()
