from __future__ import annotations

import os
import pickle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from timetable_solver import TimetableSolver


class CheckpointManager:
    def __init__(self, checkpoint_dir):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save_solver(self, solver: TimetableSolver):
        file_name = self.checkpoint_dir + "solver.pkl"
        with open(file_name, 'wb') as output:
            pickle.dump(solver, output)

    def load_solver(self):
        file_name = self.checkpoint_dir + "solver.pkl"
        with open(file_name, 'rb') as input:
            return pickle.load(input)
