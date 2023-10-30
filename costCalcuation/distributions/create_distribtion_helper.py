from costCalcuation.distributions.different_time_distribution_helper import DifferentTimeDistributionHelper
from costCalcuation.distributions.not_implemented_distribution_helper import NotImplementedDistributionHelper
from costCalcuation.distributions.same_start_distribution_helper import SameStartDistributionHelper
from costCalcuation.distributions.same_time_distribution_helper import SameTimeDistributionHelper
from models.input.distribution import Distribution
from models.input.problem import Problem


def create_helper_for_distribution(problem: Problem, distribution: Distribution):
    dist_type = distribution.type
    if dist_type == "SameStart":
        return SameStartDistributionHelper(problem, distribution)

    if dist_type == "SameTime":
        return SameTimeDistributionHelper(problem, distribution)

    if dist_type == "DifferentTime":
        return DifferentTimeDistributionHelper(problem, distribution)

    return NotImplementedDistributionHelper(problem, distribution)
