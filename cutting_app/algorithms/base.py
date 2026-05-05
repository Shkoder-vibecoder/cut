from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Sheet:
    id: int
    width: float
    height: float
    stock_sheet_id: int
    texture: str = "нет"
    index: int = 0


@dataclass
class Piece:
    id: int
    order_item_id: int
    name: str
    width: float
    height: float
    quantity: int = 1
    rotation_allowed: bool = True
    fibers: str = "any"
    priority: int = 0

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class PlacementResult:
    piece_id: int
    sheet_id: int
    x: float
    y: float
    width: float
    height: float
    rotated: bool = False


@dataclass
class CuttingParams:
    cut_width: float = 3.0
    edge_offset: float = 10.0
    cut_type: str = "свободный"
    max_guillotine_depth: float = float("inf")
    algorithm: str = "жадный"
    time_limit_seconds: Optional[float] = None
    population_size: int = 50
    generations: int = 200
    mutation_rate: float = 0.05
    crossover_rate: float = 0.85
    initial_temp: float = 1000.0
    cooling_rate: float = 0.995


@dataclass
class CuttingResult:
    placements: list[PlacementResult] = field(default_factory=list)
    kim_percent: float = 0.0
    total_sheets_used: int = 0
    total_waste_mm2: float = 0.0
    calculation_time_seconds: float = 0.0
    status: str = "ожидание"
    message: str = ""


class BaseCuttingAlgorithm(ABC):
    @abstractmethod
    def solve(
        self,
        sheets: list[Sheet],
        pieces: list[Piece],
        params: CuttingParams
    ) -> CuttingResult:
        pass

    def _calculate_kim(self, pieces: list[Piece], sheets: list[Sheet], placements: list[PlacementResult]) -> float:
        if not placements:
            return 0.0
        total_piece_area = sum(p.width * p.height for p in pieces)
        total_sheet_area = sum(s.width * s.height for s in sheets[:self._count_used_sheets(placements)])
        if total_sheet_area == 0:
            return 0.0
        return (total_piece_area / total_sheet_area) * 100

    def _count_used_sheets(self, placements: list[PlacementResult]) -> int:
        if not placements:
            return 0
        return len(set(p.sheet_id for p in placements))

    def _can_place(self, sheet_width: float, sheet_height: float, piece_w: float, piece_h: float,
                   x: float, y: float, cut_width: float, edge_offset: float) -> bool:
        return (x + piece_w + edge_offset <= sheet_width and
                y + piece_h + edge_offset <= sheet_height)

    def _sort_pieces_by_area(self, pieces: list[Piece]) -> list[Piece]:
        return sorted(pieces, key=lambda p: p.area, reverse=True)