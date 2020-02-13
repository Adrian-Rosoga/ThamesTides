import datetime
from tides import tide_data_generator_from_web, parse, TIDE_INFO_WEBPAGE_TEMPLATE, STATIONS
import pandas as pd
import matplotlib.pyplot as plt


def shifted_view(df1, dfx, delta_mins, plot = False):

    df2 = dfx.copy()

    for ix in df2.index:
        df2['Date'][ix] += pd.Timedelta(minutes=delta_mins)

    df_all = pd.merge(df1, df2, how='inner', on='Date')

    if plot:
        df_all.plot(x='Date', y=['Level_x', 'Level_y'], kind='line')
        plt.show()

    correlation = df_all.corr()['Level_x']['Level_y'] * 100

    #print(f'After shifting by {delta_mins} minutes correlation = {correlation}%')

    return correlation


def process(station_1, station_2):

    dfs = []

    for station in (station_1, station_2):
        tide_info_page = TIDE_INFO_WEBPAGE_TEMPLATE.format(station=STATIONS[station][0])

        df = pd.DataFrame(tide_data_generator_from_web(tide_info_page), columns=['Date', 'Level'])

        dfs.append(df)

    df_all = pd.merge(dfs[0], dfs[1], how='inner', on='Date')

    print(df_all)

    df_all.plot(x='Date', y=['Level_x', 'Level_y'], kind='line')

    correlation = df_all.corr()['Level_x']['Level_y'] * 100.0

    print(f'Before {correlation:.2f}%')

    shift2correlation = dict()

    for delta_mins in range(- 15 * 4 * 6, 15 * 4 * 6, 15):
        correlation = shifted_view(dfs[0], dfs[1], delta_mins)

        shift2correlation[correlation] = delta_mins

        print(f'{delta_mins} ---> {correlation:.1f}%')

    #shifted_view(dfs[0], dfs[1], -210, plot=True)
    #shifted_view(dfs[0], dfs[1], 165, plot=True)

    max_correlation = max(shift2correlation.keys())
    delta_mins_max_correlation = shift2correlation[max_correlation]

    print(f'Max correlation {max_correlation:.1f} for delta mins {delta_mins_max_correlation}')
    print(f'{delta_mins_max_correlation // 60}h {delta_mins_max_correlation % 60}m')

    shifted_view(dfs[0], dfs[1], delta_mins_max_correlation, plot=True)

    plt.show()


def main():

    #process('Chelsea', 'Dover')

    process('Chelsea', 'Westminster')


if __name__ == '__main__':

    main()
