#!/usr/bin/env python3

import sys
import datetime
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from tides import tide_data_generator_from_web, parse, TIDE_INFO_WEBPAGE_TEMPLATE, STATIONS


def get_correlation_with_shift(df1, df2, delta_mins, plot=False, message=None):

    df2_shifted = df2.copy()

    for ix in df2_shifted.index:
        df2_shifted['Date'][ix] += pd.Timedelta(minutes=delta_mins)

    df2_shifted.columns = [df2_shifted.columns[0], df2_shifted.columns[1] + ' (shifted)']

    df_all = pd.merge(df1, df2_shifted, how='inner', on='Date')

    df_all = df_all.merge(df2, how='inner', on='Date')

    if plot:
        title = 'Tide Level'
        if message is not None:
            title += '\n' + message
        df_all.plot(x='Date', y=[df_all.columns[1], df_all.columns[2], df_all.columns[3]], title=title,
                    grid=True, legend=True, figsize=(15, 10), kind='line')
        plt.show()

    correlation = df_all.corr()[df_all.columns[1]][df_all.columns[2]] * 100

    return correlation


def process(station1, station2):

    dfs = []

    for station in (station1, station2):
        tide_info_page = TIDE_INFO_WEBPAGE_TEMPLATE.format(station=STATIONS[station][0])

        df = pd.DataFrame(tide_data_generator_from_web(tide_info_page), columns=['Date', station])

        dfs.append(df)

    df_all = pd.merge(dfs[0], dfs[1], how='inner', on='Date')

    correlation = df_all.corr()[station1][station2] * 100.0

    shift2correlation = dict()

    # Magic numbers here - iterate the range plus/minus 6 hours with a 15 mins step
    for delta_mins in range(- 15 * 4 * 6, 15 * 4 * 6, 15):
        correlation_with_shift = get_correlation_with_shift(dfs[0], dfs[1], delta_mins)
        shift2correlation[correlation_with_shift] = delta_mins
        print(f'{delta_mins:3} mins ---> {correlation_with_shift:.1f}% correlation')

    max_correlation = max(shift2correlation.keys())
    delta_mins_max_correlation = shift2correlation[max_correlation]

    time_delta = f'{abs(delta_mins_max_correlation) // 60}h{abs(delta_mins_max_correlation) % 60}m'
    time_delta = f'-{time_delta}' if delta_mins_max_correlation < 0 else time_delta

    print(f'Correlation {correlation:.2f}%')
    print(f'Max correlation {max_correlation:.1f}% for time shift of {time_delta}')

    message = f'{time_delta} between peak tides at {station1} and {station2}'

    get_correlation_with_shift(dfs[0], dfs[1], delta_mins_max_correlation, plot=True, message=message)


def main():

    parser = argparse.ArgumentParser(description='Find time between high tides at two stations.\nDefault stations are Chelsea and Dover.')
    parser.add_argument('--list', help='list all stations', action='store_true')
    parser.add_argument('--station1', help='station 1')
    parser.add_argument('--station2', help='station 2')
    parser.add_argument('--noplot', help='do not show the plot on screen', action='store_true')
    parser.add_argument('--save', help='save to file', action='store_true')
    args = parser.parse_args()

    if args.list:
        for station in STATIONS.keys():
            print(station)
        sys.exit(0)

    show_plot = False if args.noplot else True
    save_to_file = False if not args.save else True

    station1 = args.station1
    station2 = args.station2

    if (station1 is None and station2 is not None) or (station1 is not None and station2 is None):
        parser.print_help(sys.stderr)
        sys.exit(1)

    if station1 is None and station2 is None:
        station1 = 'Chelsea'
        station2 = 'Dover'

    process(station1, station2)


if __name__ == '__main__':

    main()
