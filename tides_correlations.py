from tides import tide_data_generator_from_web, parse, TIDE_INFO_WEBPAGE_TEMPLATE, STATIONS
import pandas as pd
import matplotlib.pyplot as plt


def correlation(station_1, station_2):

    dfs = []

    for station in (station_1, station_2):
        tide_info_page = TIDE_INFO_WEBPAGE_TEMPLATE.format(station=STATIONS[station][0])

        df = pd.DataFrame(tide_data_generator_from_web(tide_info_page), columns=['Date', 'Level'])

        dfs.append(df)

    df_all = pd.merge(dfs[0], dfs[1], how='inner', on='Date')

    print(df_all)

    df_all.plot(x='Date', y=['Level_x', 'Level_y'], kind='line')

    correlation = df_all.corr()

    print(correlation)

    plt.show()

    return


def main():

    correlation('Chelsea', 'Dover')
    #correlation('Chelsea', 'Westminster')


if __name__ == '__main__':

    main()
