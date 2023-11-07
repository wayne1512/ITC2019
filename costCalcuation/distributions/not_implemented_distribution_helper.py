from models.input.distribution import Distribution


# temporary - used to handle distributions which are not yet implemented

class NotImplementedDistributionHelper:
    def __init__(self, problem, distribution: Distribution):
        self.problem = problem
        self.distribution = distribution

    # noinspection PyMethodMayBeStatic
    def calculate_clashes(self, rooms_option_chosen_ids, time_option_chosen_ids):
        return 0, 0

    def close_downwards_option(self, solution_search, current_row, current_option, closing_mask):
        pass
