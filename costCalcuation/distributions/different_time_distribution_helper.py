from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper


class DifferentTimeDistributionHelper(BaseDistributionHelper):
    def count_violations(self, time_options_chosen, rooms_options_chosen):
        start_times = [time_option.start for time_option in time_options_chosen]
        end_times = [time_option.start + time_option.length for time_option in time_options_chosen]

        violation_count = 0

        for i in range(len(start_times)):
            for j in range(i + 1, len(start_times)):
                if not (end_times[i] <= start_times[j] or end_times[j] <= start_times[i]):
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):
        not_different_time = []
        for time_option in checking_class.time_options:
            not_different_time.append(
                not (
                        (
                                (time_option.start + time_option.length) <= current_time_option.start
                        ) or
                        (
                                (current_time_option.start + current_time_option.length) <= time_option.start
                        )
                )
            )
        mask_sub_part_unflattened[:, not_different_time] = 1
