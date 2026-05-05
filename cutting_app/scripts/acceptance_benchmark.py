import argparse
import random
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.base import Sheet, Piece, CuttingParams
from algorithms.greedy import GreedyAlgorithm


def generate_case(piece_count: int) -> tuple[list[Sheet], list[Piece]]:
    sheets = [
        Sheet(id=i + 1, width=2800, height=2070, stock_sheet_id=i + 1, texture="none", quantity=1)
        for i in range(max(5, piece_count // 40))
    ]

    pieces = []
    for i in range(piece_count):
        w = random.randint(120, 900)
        h = random.randint(120, 800)
        pieces.append(
            Piece(
                id=i + 1,
                order_item_id=i + 1,
                name=f"P{i + 1}",
                width=float(w),
                height=float(h),
                quantity=1,
                rotation_allowed=True,
                fibers="any",
                priority=0,
            )
        )
    return sheets, pieces


def run_benchmark(piece_count: int) -> dict:
    random.seed(42)
    sheets, pieces = generate_case(piece_count)
    algo = GreedyAlgorithm()
    params = CuttingParams(cut_width=3.0, edge_offset=10.0, cut_type="free", algorithm="greedy")

    start = time.time()
    result = algo.solve(sheets, pieces, params)
    elapsed = time.time() - start

    return {
        "piece_count": piece_count,
        "elapsed_seconds": elapsed,
        "kim_percent": result.kim_percent,
        "placements": len(result.placements),
        "status": result.status,
    }


def main():
    parser = argparse.ArgumentParser(description="Acceptance benchmark for cutting app")
    parser.add_argument("--pieces", type=int, required=True, help="Piece count for benchmark")
    args = parser.parse_args()

    report = run_benchmark(args.pieces)
    print(
        f"pieces={report['piece_count']} status={report['status']} "
        f"time={report['elapsed_seconds']:.3f}s kim={report['kim_percent']:.2f}% "
        f"placed={report['placements']}"
    )


if __name__ == "__main__":
    main()
