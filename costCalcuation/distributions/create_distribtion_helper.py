import re

from costCalcuation.distributions.different_days_distribution_helper import DifferentDaysDistributionHelper
from costCalcuation.distributions.different_room_distribution_helper import DifferentRoomDistributionHelper
from costCalcuation.distributions.different_time_distribution_helper import DifferentTimeDistributionHelper
from costCalcuation.distributions.different_weeks_distribution_helper import DifferentWeeksDistributionHelper
from costCalcuation.distributions.not_implemented_distribution_helper import NotImplementedDistributionHelper
from costCalcuation.distributions.not_overlap_distribution_helper import NotOverlapDistributionHelper
from costCalcuation.distributions.overlap_distribution_helper import OverlapDistributionHelper
from costCalcuation.distributions.precedence_distribution_helper import PrecedenceDistributionHelper
from costCalcuation.distributions.same_attendees_distribution_helper import SameAttendeesDistributionHelper
from costCalcuation.distributions.same_days_distribution_helper import SameDaysDistributionHelper
from costCalcuation.distributions.same_room_distribution_helper import SameRoomDistributionHelper
from costCalcuation.distributions.same_start_distribution_helper import SameStartDistributionHelper
from costCalcuation.distributions.same_time_distribution_helper import SameTimeDistributionHelper
from costCalcuation.distributions.same_weeks_distribution_helper import SameWeeksDistributionHelper
from costCalcuation.distributions.work_days_distribution_helper import WorkDaysDistributionHelper
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

    if dist_type == "SameDays":
        return SameDaysDistributionHelper(problem, distribution)

    if dist_type == "DifferentDays":
        return DifferentDaysDistributionHelper(problem, distribution)

    if dist_type == "SameWeeks":
        return SameWeeksDistributionHelper(problem, distribution)

    if dist_type == "DifferentWeeks":
        return DifferentWeeksDistributionHelper(problem, distribution)

    if dist_type == "Overlap":
        return OverlapDistributionHelper(problem, distribution)

    if dist_type == "NotOverlap":
        return NotOverlapDistributionHelper(problem, distribution)

    if dist_type == "SameRoom":
        return SameRoomDistributionHelper(problem, distribution)

    if dist_type == "DifferentRoom":
        return DifferentRoomDistributionHelper(problem, distribution)

    if dist_type == "SameAttendees":
        return SameAttendeesDistributionHelper(problem, distribution)

    if dist_type == "Precedence":
        return PrecedenceDistributionHelper(problem, distribution)

    match = re.search("WorkDay\\((\\d+)\\)", dist_type)
    if match is not None:
        return WorkDaysDistributionHelper(problem, distribution, int(match.group(1)))

    return NotImplementedDistributionHelper(problem, distribution)
