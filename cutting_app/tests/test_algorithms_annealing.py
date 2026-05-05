import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.annealing import AnnealingAlgorithm
from algorithms.base import CuttingParams, Piece, Sheet


def test_annealing_solve_basic():
    sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
    pieces = [
        Piece(id=1, order_item_id=1, name="A", width=400, height=300),
        Piece(id=2, order_item_id=2, name="B", width=350, height=250),
        Piece(id=3, order_item_id=3, name="C", width=200, height=200),
    ]
    params = CuttingParams(
        cut_width=3.0,
        edge_offset=10.0,
        initial_temp=30.0,
        cooling_rate=0.9,
        time_limit_seconds=0.2,
    )

    result = AnnealingAlgorithm().solve(sheets, pieces, params)
    assert result.status == "done"
    assert result.kim_percent > 0
    assert len(result.placements) > 0
