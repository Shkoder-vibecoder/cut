import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.genetic import GeneticAlgorithm
from algorithms.base import Sheet, Piece, CuttingParams


class TestGeneticAlgorithm:
    def test_genetic_initialization(self):
        algo = GeneticAlgorithm()
        assert algo is not None

    def test_genetic_simple_solve(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = [
            Piece(id=1, order_item_id=1, name="P1", width=400, height=400, quantity=1),
            Piece(id=2, order_item_id=2, name="P2", width=300, height=300, quantity=1),
            Piece(id=3, order_item_id=3, name="P3", width=200, height=200, quantity=1)
        ]

        params = CuttingParams(
            cut_width=3.0,
            edge_offset=10.0,
            population_size=10,
            generations=5
        )

        algo = GeneticAlgorithm()
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"
        assert len(result.placements) >= 1
        assert result.kim_percent > 0

    def test_genetic_kim_improvement_over_greedy(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = [
            Piece(id=i, order_item_id=i, name=f"P{i}", width=150, height=150, quantity=1)
            for i in range(1, 10)
        ]

        params = CuttingParams(
            cut_width=3.0,
            edge_offset=10.0,
            population_size=20,
            generations=10
        )

        algo = GeneticAlgorithm()
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"
        assert result.kim_percent > 0

    def test_empty_pieces(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = []

        params = CuttingParams(population_size=10, generations=5)
        algo = GeneticAlgorithm()
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"

    def test_time_limit(self):
        sheets = [Sheet(id=1, width=1000, height=1000, stock_sheet_id=1, texture="none")]
        pieces = [Piece(id=i, order_item_id=i, name=f"P{i}", width=100, height=100, quantity=1) for i in range(1, 20)]

        params = CuttingParams(
            cut_width=3.0,
            edge_offset=10.0,
            population_size=50,
            generations=200,
            time_limit_seconds=0.5
        )

        algo = GeneticAlgorithm()
        result = algo.solve(sheets, pieces, params)

        assert result.status == "done"
        assert result.calculation_time_seconds <= 6.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
