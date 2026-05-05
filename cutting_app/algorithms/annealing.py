import random
import time
import numpy as np
from algorithms.base import BaseCuttingAlgorithm, Sheet, Piece, CuttingParams, CuttingResult, PlacementResult
from algorithms.greedy import GreedyAlgorithm


class AnnealingAlgorithm(BaseCuttingAlgorithm):
    def solve(self, sheets: list[Sheet], pieces: list[Piece], params: CuttingParams) -> CuttingResult:
        start_time = time.time()
        result = CuttingResult()

        sorted_pieces = self._sort_pieces_by_area(pieces)

        greedy = GreedyAlgorithm()
        current_result = greedy.solve(sheets, sorted_pieces, params)
        current_kim = current_result.kim_percent

        best_result = current_result
        best_kim = current_kim

        current_temp = params.initial_temp
        cooling_rate = params.cooling_rate
        min_temp = 1.0

        piece_ids = [p.id for p in sorted_pieces]
        iteration = 0

        while current_temp > min_temp:
            if params.time_limit_seconds and (time.time() - start_time) > params.time_limit_seconds:
                break

            new_order = piece_ids.copy()
            num_operations = random.randint(1, max(1, len(new_order) // 10))

            for _ in range(num_operations):
                if len(new_order) >= 2:
                    i, j = random.sample(range(len(new_order)), 2)
                    new_order[i], new_order[j] = new_order[j], new_order[i]

            new_pieces_order = [p for p in sorted_pieces if p.id in new_order]
            new_result = greedy.solve(sheets, new_pieces_order, params)
            new_kim = new_result.kim_percent

            delta = new_kim - current_kim

            if delta > 0 or random.random() < np.exp(delta / current_temp):
                current_result = new_result
                current_kim = new_kim
                piece_ids = new_order

                if current_kim > best_kim:
                    best_result = current_result
                    best_kim = current_kim

            current_temp *= cooling_rate
            iteration += 1

        result.placements = best_result.placements
        result.kim_percent = best_kim
        result.total_sheets_used = best_result.total_sheets_used
        result.status = "done"
        result.message = f"SA completed with KIM {result.kim_percent:.2f}% in {iteration} iterations"
        result.calculation_time_seconds = time.time() - start_time

        return result