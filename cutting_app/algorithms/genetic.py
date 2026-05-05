import random
import time
import numpy as np
from algorithms.base import BaseCuttingAlgorithm, Sheet, Piece, CuttingParams, CuttingResult, PlacementResult
from algorithms.greedy import GreedyAlgorithm, SheetState


class GeneticAlgorithm(BaseCuttingAlgorithm):
    def solve(self, sheets: list[Sheet], pieces: list[Piece], params: CuttingParams) -> CuttingResult:
        start_time = time.time()
        result = CuttingResult()

        sorted_pieces = self._sort_pieces_by_area(pieces)
        piece_ids = [p.id for p in sorted_pieces]

        population_size = params.population_size
        generations = params.generations
        mutation_rate = params.mutation_rate
        crossover_rate = params.crossover_rate

        def create_chromosome() -> list[int]:
            chrom = piece_ids.copy()
            random.shuffle(chrom)
            return chrom

        def fitness(chrom: list[int]) -> float:
            greedy = GreedyAlgorithm()
            temp_params = CuttingParams(
                cut_width=params.cut_width,
                edge_offset=params.edge_offset,
                cut_type=params.cut_type
            )
            pieces_order = [p for p in sorted_pieces if p.id in chrom]
            res = greedy.solve(sheets, pieces_order, temp_params)
            return res.kim_percent

        def pmx_crossover(parent1: list[int], parent2: list[int]) -> tuple[list[int], list[int]]:
            size = len(parent1)
            if size < 2:
                return parent1.copy(), parent2.copy()

            cx_point1 = random.randint(0, size - 2)
            cx_point2 = random.randint(cx_point1 + 1, size)

            child1 = [None] * size
            child2 = [None] * size

            child1[cx_point1:cx_point2] = parent1[cx_point1:cx_point2]
            child2[cx_point1:cx_point2] = parent2[cx_point1:cx_point2]

            for i in range(size):
                if child1[i] is None:
                    val = parent2[i]
                    while val in child1:
                        idx = parent2.index(val)
                        val = parent1[idx]
                    child1[i] = val

                if child2[i] is None:
                    val = parent1[i]
                    while val in child2:
                        idx = parent1.index(val)
                        val = parent2[idx]
                    child2[i] = val

            return child1, child2

        def mutate(chrom: list[int]) -> list[int]:
            if random.random() < mutation_rate and len(chrom) >= 2:
                i, j = random.sample(range(len(chrom)), 2)
                chrom[i], chrom[j] = chrom[j], chrom[i]
            return chrom

        def tournament_select(population: list[list[int]], fitnesses: list[float], k: int = 3) -> list[int]:
            selected = random.sample(list(zip(population, fitnesses)), k)
            return max(selected, key=lambda x: x[1])[0]

        if not piece_ids:
            result.status = "done"
            result.message = "No pieces to cut"
            result.calculation_time_seconds = time.time() - start_time
            return result

        population = [create_chromosome() for _ in range(population_size)]
        fitnesses = [fitness(chrom) for chrom in population]

        best_chrom = max(zip(population, fitnesses), key=lambda x: x[1])[0]
        best_fitness = max(fitnesses)

        for gen in range(generations):
            new_population = []
            new_population.append(best_chrom.copy())

            while len(new_population) < population_size:
                p1 = tournament_select(population, fitnesses, 3)
                p2 = tournament_select(population, fitnesses, 3)

                if random.random() < crossover_rate:
                    c1, c2 = pmx_crossover(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()

                new_population.append(mutate(c1))
                if len(new_population) < population_size:
                    new_population.append(mutate(c2))

            population = new_population[:population_size]
            fitnesses = [fitness(chrom) for chrom in population]

            current_best_idx = np.argmax(fitnesses)
            if fitnesses[current_best_idx] > best_fitness:
                best_fitness = fitnesses[current_best_idx]
                best_chrom = population[current_best_idx].copy()

            if params.time_limit_seconds and (time.time() - start_time) > params.time_limit_seconds:
                break

        greedy = GreedyAlgorithm()
        pieces_order = [p for p in sorted_pieces if p.id in best_chrom]
        final_result = greedy.solve(sheets, pieces_order, params)

        result.placements = final_result.placements
        result.kim_percent = final_result.kim_percent
        result.total_sheets_used = final_result.total_sheets_used
        result.status = "done"
        result.message = f"GA completed with KIM {result.kim_percent:.2f}%"
        result.calculation_time_seconds = time.time() - start_time

        return result