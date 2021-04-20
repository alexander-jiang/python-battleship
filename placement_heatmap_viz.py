import click
import random
import time
import seaborn as sns
import matplotlib.pylab as plt
import numpy as np
from typing import List, Optional, Tuple

from game_state import STANDARD_SHIP_DIMENSIONS
from ship_placement import random_ships_placement


NUM_ROWS = 10
NUM_COLS = 10


def compute_symmetries(square_numpy_array: np.ndarray) -> List[np.ndarray]:
    assert len(square_numpy_array.shape) == 2
    assert square_numpy_array.shape[0] == square_numpy_array.shape[1]

    symmetry = square_numpy_array.copy()
    return []


def compute_placement_distribution(
    ship_dims: List[Tuple[int, int]], num_iterations: int, with_symmetries: bool = False
) -> np.ndarray:
    sampled_placements = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.uint32)
    num_samples = 0
    start_time = time.time()
    for iter_num in range(num_iterations):
        if (iter_num + 1) % 10000 == 0:
            print(f"Iteration number {iter_num + 1} of {num_iterations}")
            end_time = time.time()
            print(f"average rate = {(iter_num + 1) / (end_time - start_time)}")

        available_squares = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.bool8)
        available_squares.fill(True)
        available_squares = available_squares.tolist()

        # TODO placement with ascending ship dims is taking too long, need to fix
        placements = random_ships_placement(
            ship_dims=ship_dims,
            available_squares=available_squares,
            num_rows=NUM_ROWS,
            num_cols=NUM_COLS,
            rotate_allowed=True,
        )

        ship_squares = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.uint32)
        for top_row_idx, left_col_idx, ship_height, ship_width in placements:
            ship_squares[
                top_row_idx : top_row_idx + ship_height,
                left_col_idx : left_col_idx + ship_width,
            ] += 1

        # TODO calculate symmetries (maybe not necessary, given that 1 million iterations 
        # with ship dims in descending order is pretty fast and seems pretty even)

        # TODO analyze exactly how asymmetrical the heatmap/distribution is (without symmetry)

        if with_symmetries:
            raise NotImplementedError
        else:
            sampled_placements += ship_squares
            num_samples += 1

    return sampled_placements / num_samples


def generate_placement_distributions(
    ship_dims: List[Tuple[int, int]],
    num_iterations: int,
    with_symmetry: bool,
    random_seed: Optional[int],
):
    if random_seed is not None:
        random.seed(random_seed)

    placement_distribution = compute_placement_distribution(
        ship_dims=ship_dims,
        num_iterations=num_iterations,
        with_symmetries=with_symmetry,
    )
    return placement_distribution


@click.command()
@click.option("--num-iterations", "-n", type=int, required=True)
@click.option("--ship-dims-file", "-i", type=str, required=True)
@click.option("--with-symmetry", is_flag=True)
@click.option("--random-seed", "-r", type=int)
@click.option("--out-file-prefix", "-o", type=str)
def cli(
    num_iterations: int,
    ship_dims_file: str,
    with_symmetry: bool,
    random_seed: Optional[int],
    out_file_prefix: Optional[str],
):
    ship_dims = []
    with open(ship_dims_file, "r") as in_file:
        for line in in_file.readlines():
            dims = [int(token.strip()) for token in line.split(",")]
            ship_dims.append(tuple(dims))

    placement_distribution = generate_placement_distributions(
        ship_dims, num_iterations, with_symmetry, random_seed
    )

    if out_file_prefix is not None:
        # save numpy array to file output in binary .npy format
        np.save(out_file_prefix + ".npy", placement_distribution)

    ax = sns.heatmap(placement_distribution, linewidth=0.5)
    plt.savefig(out_file_prefix + ".jpg")
    plt.show()


if __name__ == "__main__":
    cli()