import sys
import datetime
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from tides import tide_data_generator_from_web, parse, TIDE_INFO_WEBPAGE_TEMPLATE, STATIONS


def shifted_view(df1, df2, delta_mins, plot=False):

    df2_shifted = df2.copy()

    for ix in df2_shifted.index:
        df2_shifted['Date'][ix] += pd.Timedelta(minutes=delta_mins)

    df2_shifted.columns = [df2_shifted.columns[0], df2_shifted.columns[1] + ' (shifted)']

    df_all = pd.merge(df1, df2_shifted, how='inner', on='Date')

    df_all = df_all.merge(df2, how='inner', on='Date')

    if plot:
        df_all.plot(x='Date', y=[df_all.columns[1], df_all.columns[2], df_all.columns[3]], title='Tide Level', figsize=(15, 10), kind='line')
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

    print(f'Correlation {correlation:.2f}%')

    shift2correlation = dict()

    for delta_mins in range(- 15 * 4 * 6, 15 * 4 * 6, 15):
        correlation = shifted_view(dfs[0], dfs[1], delta_mins)

        shift2correlation[correlation] = delta_mins

        print(f'{delta_mins} ---> {correlation:.1f}%')

    max_correlation = max(shift2correlation.keys())
    delta_mins_max_correlation = shift2correlation[max_correlation]

    print(f'Max correlation {max_correlation:.1f}% for shift of {delta_mins_max_correlation // 60}h {delta_mins_max_correlation % 60}m')

    shifted_view(dfs[0], dfs[1], delta_mins_max_correlation, plot=True)


def main():

    process('Chelsea', 'Dover')

    # process('Chelsea', 'Westminster')

    # process('Chelsea', 'Tower Pier')


if __name__ == '__main__':

    main()
