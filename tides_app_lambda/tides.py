#!/usr/bin/env python3


import pytz
import sys
import time
import datetime
import requests
import argparse
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#
# Adrian Rosoga, 19 Jan 2020
#
# Example @ Westminster: https://flood-warning-information.service.gov.uk/station/7389
#


# station_name -> (station_id, description)
STATIONS = {'Dover': (1158, 'Dover'),
            'Southend': (7386, 'Southend'),
            'Sheerness': (1157, 'Sheerness'),
            'Tilbury': (7394, 'Tilbury'),
            'Silvertown': (7388, 'Silvertown'),
            'Tower Pier': (7391, 'Thames at Tower Pier'),
            'Westminster': (7389, 'Thames at Westminster'),
            'Chelsea': (7392, 'Thames at Chelsea'),
            'Richmond': (7393, 'Thames at Richmond')
            }


TIDE_INFO_WEBPAGE_TEMPLATE = 'https://flood-warning-information.service.gov.uk/station/{station}'
RECORDS_DIR = 'records'  # Directory where figures are saved - relative to the script location directory
MINUTES_TO_SLEEP = 10


def london_time(timestring):

    tz = pytz.timezone('UTC')
    naive_time = datetime.datetime.strptime(timestring, "%Y-%m-%dT%H:%MZ")
    tz_time = tz.localize(naive_time)
    london_tz = pytz.timezone('Europe/London')
    london_time = tz_time.astimezone(london_tz)

    return london_time


def tide_data_generator_from_web(tide_info_page: str):

    page = requests.get(tide_info_page)

    if page.status_code != requests.codes.ok:
        print(f'Couldn\'t open the web page {tide_info_page}')
        raise StopIteration

    return parse(page.text)


def tide_data_generator_from_file(filename: str):

    with open(filename) as f:
        return parse(f.read())


def parse(file_content):

    """
    <tr>
         <td scope="row"><time datetime="2020-01-14T17:15Z">2020-01-14T17:15Z</time></td>
         <td class="numeric">3.622</td>
         <td>false</td>
    </tr>
    """

    soup = BeautifulSoup(file_content, features="lxml")
    rows = soup.find_all('tr')

    # Reverse the order as latest data comes first
    for row in reversed(rows):
        timestamp = row.find('time')
        if timestamp:
            timestamp_obj = london_time(timestamp.text)
            water_level = row.find('td', {"class": "numeric"})
            yield timestamp_obj, float(water_level.text)


def process(generator, station='', show_plot=True, save_to_file=False, all_five_days=False, save_plot_png=False):

    dates = []
    levels = []

    for timestamp, level in generator:
        dates.append(timestamp)
        levels.append(level)

    if not all_five_days:
        # Analize only the last 2 days
        dates = dates[4 * 24 * 4:]
        levels = levels[4 * 24 * 4:]

    if len(dates) == 0:
        print('No data!')
        return

    tide_speed_cm_per_min = [(l2 - l1) * 100.0 / 15.0 for l2, l1 in zip(levels[1:], levels[:-1])]

    if False:
        for date, level, speed in zip(dates, levels, tide_speed_cm_per_min):
            print(f'{date}: Level={level:5.2f}m   Rise={speed:5.2f}cm/min')

    print('\n'.join((f'\n=== {station} from {dates[0]} to {dates[-1]}\n',
                     f'Current datetime {dates[-1]}',
                     f'Current level {levels[-1]:.1f}m',
                     f'Current tide speed {tide_speed_cm_per_min[-1]:.1f}cm/min',
                     f'Max level {max(levels):.1f}m',
                     f'Min level {min(levels):.1f}m',
                     f'Avg level {sum(levels)/len(levels):.1f}m',
                     f'Amplitude {max(levels) - min(levels):.1f}m',
                     f'Max tide rise speed {max(tide_speed_cm_per_min):.1f}cm/min',
                     f'Max tide decrease speed {min(tide_speed_cm_per_min):.1f}cm/min')))

    plot(station, dates, levels, tide_speed_cm_per_min, show_plot, save_to_file, all_five_days, save_plot_png)


def plot(station, dates, levels, tide_speed_cm_per_min, show_plot, save_to_file, all_five_days=False, save_plot_png=False):

    # Colors from http://ksrowell.com/blog-visualizing-data/2012/02/02/optimal-colors-for-graphs/
    water_color = '#396AB1'
    tide_rise_color = '#DA7C30'
    title_color = '#535154'
    box_background_color = '#CCC210'

    station_description = STATIONS[station][1]

    figure = plt.figure(figsize=(20, 10))
    plot = figure.add_subplot(111)

    plot.plot(dates, levels, water_color, marker='.', linewidth=3.0, label='Water level')

    plt.ylabel('Water level (m)', color=water_color, fontweight='bold', fontsize=22)

    plot2 = plot.twinx()

    plot2.plot(dates[:-1], tide_speed_cm_per_min, tide_rise_color, marker='.', linewidth=0.5, label='Tide rise speed')

    # Grid
    plot.axhline(linewidth=1, color='r')
    plot.grid(color='g', linestyle=':', linewidth=0.5)

    plt.xlabel('Date')

    plot.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plot2.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')

    plt.ylabel('Tide rise speed (cm/min)', color=tide_rise_color, fontweight='bold', fontsize=22)

    # Mark the last point on each graph
    plot.scatter(dates[-1], levels[-1], marker='o', s=400, c=water_color)
    plot2.scatter(dates[-2], tide_speed_cm_per_min[-1], marker='o', s=400, c=tide_rise_color)

    title_font = {'family': 'serif',
                  'color': title_color,
                  'weight': 'bold',
                  'size': 24, }

    # Title
    plt.title(f'{station_description}\nFrom {dates[0]} to {dates[-1]}', fontdict=title_font)

    # Rotate the x axis to avoid overlapping
    for label in plot.get_xticklabels() + plot2.get_xticklabels():
        label.set_rotation(30)
        label.set_ha('right')
        label.set_fontsize(12)

    # Format of date on x axis
    ax = plt.gca()
    xaxisFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    ax.xaxis.set_major_formatter(xaxisFmt)

    # Info about levels
    level_info_box = plt.text(dates[0], 0,
                              f'Now={levels[-1]:.1f}m\n(Min={min(levels):.1f}m Max={max(levels):.1f}m'
                              f' Avg={(sum(levels)/len(levels)):.1f}m Delta={(max(levels) - min(levels)):.1f}m',
                              fontsize=32)
    level_info_box.set_bbox(dict(facecolor=box_background_color, alpha=1, edgecolor=box_background_color))

    # Legend
    plot.legend(loc='upper left', fontsize='x-large')
    plot2.legend(loc='upper right', fontsize='x-large')

    # Save to file
    if save_to_file:
        number_days = 5 if all_five_days else 2

        if save_plot_png:
            pathname = "plot.png"
        else:
            last_date = str(dates[-1]).replace(':', '-')
            filename = f'{station_description}_{last_date}_{number_days}_days.png'.replace(' ', '_')
            pathname = f'{RECORDS_DIR}/{filename}'

        try:
            plt.savefig(f'{pathname}', dpi=300)
            print(f'\nSaved graph as {pathname}')
        except FileNotFoundError:
            print(f'\nError: Couldn\'t save graph as {pathname}')

    if show_plot:
        plt.show()


def process_from_web(station: str, show_plot=True, save_to_file=False, all_five_days=False, save_plot_png=False):

    tide_info_page = TIDE_INFO_WEBPAGE_TEMPLATE.format(station=STATIONS[station][0])

    process(tide_data_generator_from_web(tide_info_page), station, show_plot, save_to_file, all_five_days, save_plot_png)


def process_from_file(station: str, filename: str, show_plot=True, save_to_file=False, all_five_days=False, save_plot_png=False):

    process(tide_data_generator_from_file(filename), station, show_plot, save_to_file, all_five_days, save_plot_png)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tides')
    parser.add_argument('--list', help='list all stations', action='store_true')
    parser.add_argument('--all', help='show all stations', action='store_true')
    parser.add_argument('--station', help='station to show')
    parser.add_argument('--file', help='process from file (testing purposes)')
    parser.add_argument('--noplot', help='do not show the plot on screen', action='store_true')
    parser.add_argument('--save', help='save to file', action='store_true')
    parser.add_argument('--five', help='all (five) days', action='store_true')
    parser.add_argument(f'--continuous', help='repeat every {MINUTES_TO_SLEEP} mins', action='store_true')
    parser.add_argument('--save_plot_png', help='save as plot.png', action='store_true')
    args = parser.parse_args()

    if args.list:
        for station in STATIONS.keys():
            print(station)
        sys.exit(0)

    all_five_days = True if args.five else False

    show_plot = False if args.noplot else True
    save_to_file = False if not args.save else True
    save_plot_png = False if not args.save_plot_png else True

    # Fallback - Chelsea is nearer until Westminster comes back online (down Feb 2020)
    station = args.station if args.station else 'Chelsea'

    if args.all:
        for station in STATIONS:
            process_from_web(station, show_plot=show_plot, save_to_file=save_to_file,
                             all_five_days=all_five_days, save_plot_png=save_plot_png)
        sys.exit(0)

    if args.file:
        process_from_file('STATION', args.file, show_plot=show_plot,
                          save_to_file=save_to_file,
                          all_five_days=all_five_days,
                          save_plot_png=save_plot_png)
        sys.exit(0)

    if args.continuous:
        while True:
            process_from_web(station, show_plot=False, save_to_file=save_to_file, all_five_days=all_five_days)
            print(f'Sleeping {MINUTES_TO_SLEEP} minutes...')
            time.sleep(MINUTES_TO_SLEEP * 60)

    process_from_web(station, show_plot=show_plot, save_to_file=save_to_file,
                     all_five_days=all_five_days, save_plot_png=save_plot_png)
