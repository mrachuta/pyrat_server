# -*- coding: utf-8 -*-


def get_diff(time_bigger, time_smaller):

    def prepare_time(unf_time):
        unf_time = unf_time.replace(' ', '-').replace(':', '-').split('-')
        unf_time = [int(c) for c in unf_time]
        return unf_time

    time_bigger = prepare_time(time_bigger)
    time_smaller = prepare_time(time_smaller)

    time_diff = [int(time_bigger[i]) - int(time_smaller[i]) for i in range(len(time_bigger))]

    td_1 = int(time_diff[2] * 86400)
    td_2 = int(time_diff[3] * 3600)
    td_3 = int(time_diff[4] * 60)
    td_4 = time_diff[5]
    td_5 = 7200 # difference between remote PC local time and server time (UTC)

    real_diff = td_1 + td_2 + td_3 + td_4 + td_5

    if real_diff > 300:
        info = 'Timed out \n>300'
    else:
        info = real_diff

    return info