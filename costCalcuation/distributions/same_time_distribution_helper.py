from costCalcuation.distributions.base_distribution_helper import BaseDistributionHelper


class SameTimeDistributionHelper(BaseDistributionHelper):
    def count_violations(self, time_options_chosen, rooms_options_chosen):
        start_times = [time_option.start for time_option in time_options_chosen]
        end_times = [time_option.start + time_option.length for time_option in time_options_chosen]

        violation_count = 0

        for i in range(len(start_times)):
            for j in range(i + 1, len(start_times)):
                if not ((start_times[i] <= start_times[j] and end_times[j] <= end_times[i])
                        or (start_times[j] <= start_times[i] and end_times[i] <= end_times[j])):
                    violation_count += 1

        return violation_count

    def close_options_for_checking_class(self, current_class, current_room_option, current_time_option, checking_class,
                                         mask_sub_part_unflattened):

        not_same_time = []
        for time_option in checking_class.time_options:
            not_same_time.append(
                not (
                        (
                                current_time_option.start <= time_option.start and (
                                time_option.start + time_option.length) <= (
                                        current_time_option.start + current_time_option.length)
                        )
                        or (
                                time_option.start <= current_time_option.start and (
                                current_time_option.start + current_time_option.length) <= (
                                        time_option.start + time_option.length)
                        )
                )
            )
        mask_sub_part_unflattened[:, not_same_time] = 1
