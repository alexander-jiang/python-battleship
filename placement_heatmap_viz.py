import click
import random
import seaborn as sns
import matplotlib.pylab as plt
import numpy as np
from typing import List, Optional, Tuple

from game_state import STANDARD_SHIP_DIMENSIONS
from ship_placement import random_ships_placement


# NUM_ITERATIONS = 1_000
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
    for iter_num in range(num_iterations):
        if (iter_num + 1) % 100 == 0:
            print(f"Iteration number {iter_num + 1} of {num_iterations}")
        available_squares = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.bool8)
        available_squares.fill(True)
        available_squares = available_squares.tolist()

        # TODO placement with ascending ship dims is taking too long, need to fix
        # option 1: add a timeout (but does that affect the distribution of overall placements)
        # option 2: in the random ship placement, enumerate all possible options for each ship 
        #  and pick randomly from those instead of retrying until one fits (also has benefit of detecting
        #  if no placement is possible)
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

        # print("placements:")
        # print(ship_squares)

        # print("total samples:")
        # print(sampled_placements)

        # TODO calculate symmetries
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
@click.option("--out-file", "-o", type=str)
def cli(
    num_iterations: int,
    ship_dims_file: str,
    with_symmetry: bool,
    random_seed: Optional[int],
    out_file: Optional[str],
):
    ship_dims = []
    with open(ship_dims_file, "r") as in_file:
        for line in in_file.readlines():
            dims = [int(token.strip()) for token in line.split(",")]
            ship_dims.append(tuple(dims))

    placement_distribution = generate_placement_distributions(
        ship_dims, num_iterations, with_symmetry, random_seed
    )

    if out_file is not None:
        # save numpy array to file output in binary .npy format
        np.save(out_file, placement_distribution)

    ax = sns.heatmap(placement_distribution, linewidth=0.5)
    plt.show()


if __name__ == "__main__":
    cli()