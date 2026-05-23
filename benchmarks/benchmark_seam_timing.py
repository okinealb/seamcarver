"""Benchmark seam removal time for random images of various sizes.

This script generates random RGB images at small, medium, and large resolutions,
then measures and plots the total time to remove an increasing number of seams.
The graph visualizes seam count (x-axis) vs. elapsed time (y-axis) for each size.

Requires: numpy, Pillow, matplotlib

Usage:
    python benchmarks/benchmark_seam_timing.py

Results are saved as 'benchmarks/removal_benchmark.png'.
"""

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import os
import sys

# Finds the absolute path of the parent directory and adds it to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from seamcarver import SeamCarver, VERTICAL

IMAGE_SIZES = {
    "Small (256x256)": (256, 256),
    "Medium (512x512)": (512, 512),
    "Large (1024x1024)": (1024, 1024),
}
SEAM_COUNTS = [10, 20, 40, 80, 160]


def generate_random_image(size: tuple[int, int]) -> np.ndarray:
    """Generate a random RGB image as a numpy array."""
    return np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)


def benchmark_seam_removal(image_array: np.ndarray, num_seams: int) -> float:
    """Measure total time to remove given number of vertical seams."""
    img = image_array.copy()
    sc = SeamCarver(img)
    start = time.perf_counter()
    sc.remove(direction=VERTICAL, num_seams=num_seams)
    elapsed = time.perf_counter() - start
    return elapsed


def main() -> None:
    np.random.seed(42)
    results: dict[str, list[float]] = {size_label: [] for size_label in IMAGE_SIZES}
    for size_label, size in IMAGE_SIZES.items():
        image = generate_random_image(size)
        print(f"Benchmarking {size_label}...")
        for seams in SEAM_COUNTS:
            t = benchmark_seam_removal(image, seams)
            print(f"  {seams} seams: {t:.3f} s")
            results[size_label].append(t)

    plt.figure(figsize=(8, 6))
    for size_label in IMAGE_SIZES:
        plt.plot(SEAM_COUNTS, results[size_label], marker="o", label=size_label)
    plt.title("Seam Removal Time vs. Number of Seams")
    plt.xlabel("Number of vertical seams removed")
    plt.ylabel("Elapsed time (seconds)")
    plt.legend()
    plt.grid(True)
    out_path = Path(__file__).parent / "benchmark_graph.png"
    plt.savefig(out_path)
    print(f"Saved plot to {out_path}")


if __name__ == "__main__":
    main()
