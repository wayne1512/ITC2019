import re

from costCalcuation.distributions.ITC2007_max_consecutive_distribution_helper import \
    ITC2007MaxConsecutiveDistributionHelper
from costCalcuation.distributions.ITC2007_min_day_load_distribution_helper import ITC2007MinDayLoadDistributionHelper
from costCalcuation.distributions.ITC2007_min_days_distribution_helper import ITC2007MinDaysDistributionHelper
from costCalcuation.distributions.ITC2007_not_isoltated_helper import ITC2007NotIsolatedDistributionHelper
from costCalcuation.distributions.ITC2007_same_room import ITC2007SameRoomDistributionHelper
from costCalcuation.distributions.different_days_distribution_helper import DifferentDaysDistributionHelper
from costCalcuation.distributions.different_room_distribution_helper import DifferentRoomDistributionHelper
from costCalcuation.distributions.different_time_distribution_helper import DifferentTimeDistributionHelper
from costCalcuation.distributions.different_weeks_distribution_helper import DifferentWeeksDistributionHelper
from costCalcuation.distributions.max_block_distribution_helper import MaxBlockDistributionHelper
from costCalcuation.distributions.max_breaks_distribution_helper import MaxBreaksDistributionHelper
from costCalcuation.distributions.max_day_load_distribution_helper import MaxDayLoadDistributionHelper
from costCalcuation.distributions.max_days_distribution_helper import MaxDaysDistributionHelper
from costCalcuation.distributions.min_gap_distribution_helper import MinGapDistributionHelper
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

    if dist_type == "ITC2007SameRoom":
        return ITC2007SameRoomDistributionHelper(problem, distribution)

    if dist_type == "DifferentRoom":
        return DifferentRoomDistributionHelper(problem, distribution)

    if dist_type == "SameAttendees":
        return SameAttendeesDistributionHelper(problem, distribution)

    if dist_type == "Precedence":
        return PrecedenceDistributionHelper(problem, distribution)

    if dist_type == "ITC2007NotIsolated":
        return ITC2007NotIsolatedDistributionHelper(problem, distribution)

    match = re.search("WorkDay\\((\\d+)\\)", dist_type)
    if match is not None:
        return WorkDaysDistributionHelper(problem, distribution, int(match.group(1)))

    match = re.search("MinGap\\((\\d+)\\)", dist_type)
    if match is not None:
        return MinGapDistributionHelper(problem, distribution, int(match.group(1)))

    match = re.search("MaxDays\\((\\d+)\\)", dist_type)
    if match is not None:
        return MaxDaysDistributionHelper(problem, distribution, int(match.group(1)))

    match = re.search("MaxDayLoad\\((\\d+)\\)", dist_type)
    if match is not None:
        return MaxDayLoadDistributionHelper(problem, distribution, int(match.group(1)))

    match = re.search("MaxBreaks\\((\\d+),(\\d+)\\)", dist_type)
    if match is not None:
        return MaxBreaksDistributionHelper(problem, distribution, int(match.group(1)), int(match.group(2)))

    match = re.search("MaxBlock\\((\\d+),(\\d+)\\)", dist_type)
    if match is not None:
        return MaxBlockDistributionHelper(problem, distribution, int(match.group(1)), int(match.group(2)))

    match = re.search("ITC2007MaxConsecutive\\((\\d+)\\)", dist_type)
    if match is not None:
        return ITC2007MaxConsecutiveDistributionHelper(problem, distribution, int(match.group(1)))

    match = re.search("ITC2007MinDayLoad\\((\\d+)\\)", dist_type)
    if match is not None:
        return ITC2007MinDayLoadDistributionHelper(problem, distribution, int(match.group(1)))

    match = re.search("ITC2007MinDays\\((\\d+)\\)", dist_type)
    if match is not None:
        return ITC2007MinDaysDistributionHelper(problem, distribution, int(match.group(1)))

    return NotImplementedDistributionHelper(problem, distribution)
