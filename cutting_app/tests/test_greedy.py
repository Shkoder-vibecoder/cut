import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.greedy import GreedyAlgorithm, SheetState
from algorithms.base import Sheet, Piece, CuttingParams


class TestGreedyAlgorithm:
    def test_simple_placement(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = [Piece(id=1, order_item_id=1, name="Test", width=500, height=500, quantity=1)]

        algo = GreedyAlgorithm()
        params = CuttingParams(cut_width=3.0, edge_offset=10.0)
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"
        assert len(result.placements) == 1
        assert result.placements[0].x == 10
        assert result.placements[0].y == 10

    def test_multiple_pieces(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = [
            Piece(id=1, order_item_id=1, name="Large", width=600, height=400, quantity=1),
            Piece(id=2, order_item_id=2, name="Medium", width=300, height=300, quantity=1),
            Piece(id=3, order_item_id=3, name="Small", width=200, height=200, quantity=1)
        ]

        algo = GreedyAlgorithm()
        params = CuttingParams(cut_width=3.0, edge_offset=10.0)
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"
        assert len(result.placements) == 3

    def test_rotation_allowed(self):
        sheets = [Sheet(id=1, width=500, height=800, stock_sheet_id=1, texture="none")]
        pieces = [Piece(id=1, order_item_id=1, name="Rotatable", width=700, height=300, rotation_allowed=True, quantity=1)]

        algo = GreedyAlgorithm()
        params = CuttingParams(cut_width=3.0, edge_offset=10.0)
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"
        assert len(result.placements) == 1

    def test_kim_calculation(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = [Piece(id=1, order_item_id=1, name="Test", width=500, height=500, quantity=1)]

        algo = GreedyAlgorithm()
        params = CuttingParams(cut_width=0, edge_offset=0)
        result = algo.solve(sheets, pieces, params)

        assert result.kim_percent == pytest.approx(25.0, rel=0.01)

    def test_empty_pieces(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = []

        algo = GreedyAlgorithm()
        params = CuttingParams()
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"
        assert len(result.placements) == 0


class TestSheetState:
    def test_can_place_empty_sheet(self):
        state = SheetState(1, 1000, 1000, 1, "none")
        assert state.can_place(0, 0, 500, 500, 3.0, 10.0) is True

    def test_cannot_place_overlapping(self):
        state = SheetState(1, 1000, 1000, 1, "none")
        state.add_placement(0, 0, 500, 500, 3.0)
        assert state.can_place(400, 400, 200, 200, 3.0, 10.0) is False

    def test_can_place_with_cut_width(self):
        state = SheetState(1, 1000, 1000, 1, "none")
        state.add_placement(0, 0, 500, 500, 3.0)
        assert state.can_place(503, 0, 200, 200, 3.0, 10.0) is True

    def test_edge_offset_respected(self):
        sheets = [Sheet(id=1, width=200, height=200, stock_sheet_id=1, texture="none")]
        pieces = [Piece(id=1, order_item_id=1, name="P", width=190, height=190, quantity=1)]

        algo = GreedyAlgorithm()
        params = CuttingParams(cut_width=0, edge_offset=10)
        result = algo.solve(sheets, pieces, params)

        assert len(result.placements) == 0

    def test_guillotine_constraint_check(self):
        state = SheetState(1, 1000, 1000, 1, "none")
        state.add_placement(10, 10, 400, 400, 3.0)
        assert state.can_place_guillotine(100, 100, 3.0, 10.0, 1000.0) is True

    def test_guillotine_depth_limit(self):
        state = SheetState(1, 1000, 1000, 1, "none")
        assert state.can_place_guillotine(100, 300, 3.0, 10.0, 200.0) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
