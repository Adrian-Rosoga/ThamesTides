import re
import sys
import datetime
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#
# Adrian Rosoga, 19 Jan 2020
#
# Westminster
# https://flood-warning-information.service.gov.uk/station/7389
# Chelsea
# https://flood-warning-information.service.gov.uk/station/7392
#
# <tr>
#     <td scope="row"><time datetime="2020-01-14T17:15Z">2020-01-14T17:15Z</time></td>
#     <td class="numeric">3.622</td>
#     <td>false</td>
# </tr>


STATIONS = {'Dover': 1158,
            'Southend': 7386,
            'Sheerness': 1157,
            'Tilbury': 7394,
            'Silvertown': 7388,
            'Tower Pier': 7391,
            'Westminster': 7389,
            'Chelsea': 7392,
            'Richmond': 7393}


tide_info_webpage_template = 'https://flood-warning-information.service.gov.uk/station/{station}'


def tide_data_generator_from_web(tide_info_page: str):

    page = requests.get(tide_info_page)

    if page.status_code != requests.codes.ok:
        print('Error')
        raise StopIteration

    # TODO - Extract only relevant info
    # soup = BeautifulSoup(page.text, 'html.parser')
    # items = soup.find_all('tr')

    for line in page.text.split('\n'):
        yield line


def tide_data_generator_from_file(filename: str):

    with open(filename) as f:
        for line in f:
            yield line


def process(lines, station='', show_plot=False):

    date_levels = []
    for line in lines:

        DATETIME_RE = r"<time.*>(.*)</time>"
        m = re.search(DATETIME_RE, line)
        if m:
            datetime_str = m[1]
            datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%MZ')

            next_line = next(lines)
            LEVEL_RE = r"<td class=\"numeric\">(.*)</td>"
            m = re.search(LEVEL_RE, next_line)
            if m:
                level = float(m[1])

                # date_levels.append([datetime_obj, level])
                date_levels.insert(0, [datetime_obj, level])

    # Analize only the first 2 days
    # date_levels = date_levels[:4 * 24 * 2]

    # Analize only the first day
    # date_levels = date_levels[:4 * 24 * 1]

    # Analize only the last 2 days
    date_levels = date_levels[4 * 24 * 4:]

    dates = [date for date, _ in date_levels]
    levels = [level for _, level in date_levels]

    tide_speed_cm_per_min = [(l2 - l1) * 100.0 / 15.0 for l2, l1 in zip(levels[1:], levels[:-1])]

    if False:
        for date, level, speed in zip(dates, levels, tide_speed_cm_per_min):
            print(f"{date}: Level={level:5.2f} m   Rise={speed:5.2f} cm/min")

    print("")
    print(f'=== {station}')
    print(f"Maximum level {max(levels)} m")
    print(f"Minimum level {min(levels)} m")
    print(f"Delta {max(levels) - min(levels):.1f} m")
    print(f"Maximum vertical speed {max(tide_speed_cm_per_min):.2f} cm per min")
    print(f"Minimum vertical speed {min(tide_speed_cm_per_min):.2f} cm per min")
    print(f"From {date_levels[0][0]} to {date_levels[len(date_levels) - 1][0]}")

    plot(station, dates, levels, tide_speed_cm_per_min, show_plot)


def plot(station, dates, levels, tide_speed_cm_per_min, show_plot):

    figure = plt.figure(figsize=(20, 10))
    plot = figure.add_subplot(111)

    plot.plot(dates, levels, 'blue', marker="*", label="Water level")

    plt.ylabel("Water level (m)", color='blue', fontweight='bold', fontsize=17)

    plot2 = plot.twinx()

    plot2.plot(dates[:-1], tide_speed_cm_per_min, 'orange', marker=".", linewidth=0.5, label="Tide rise speed")

    plot.axhline(linewidth=1, color='r')
    plot.grid(color='g', linestyle=':', linewidth=0.5)

    plt.xlabel("Date")

    plot.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plot2.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')

    plt.ylabel("Tide rise speed (cm/min)", color='orange', fontweight='bold', fontsize=17)

    # Mark the last point on each graph
    plot.scatter(dates[-1], levels[-1], marker='o', s=400, c='blue')
    plot2.scatter(dates[-2], tide_speed_cm_per_min[-1], marker='o', s=400, c='blue')

    title_font = {'family': 'serif',
                  'color': 'black',
                  'weight': 'bold',
                  'size': 16, }

    # Title
    plt.title(f'Thames at {station} (2 days)\n{dates[-1]}', fontdict=title_font)

    # Rotate the x axis to avoid overlapping
    for label in plot.get_xticklabels() + plot2.get_xticklabels():
        label.set_rotation(30)
        label.set_ha('right')

    # Info about levels
    level_info_box = plt.text(dates[0], 0,
                              f'min={min(levels):.1f}m max={max(levels):.1f} delta={(max(levels) - min(levels)):.1f}m',
                              fontsize=22)
    level_info_box.set_bbox(dict(facecolor='yellow', alpha=1, edgecolor='blue'))

    plot.legend(loc='upper left', fontsize='x-large')
    plot2.legend(loc='upper right', fontsize='x-large')

    # Save to file
    last_date = str(dates[-1]).replace(' ', '_').replace(':', '-')
    plt.savefig(f'records/Thames_at_{station}_{last_date}.png', dpi=300)

    if show_plot:
        plt.show()


def process_from_web(station: str, show_plot=True):

    tide_info_page = tide_info_webpage_template.format(station=STATIONS[station])
    lines = (line for line in tide_data_generator_from_web(tide_info_page))

    process(lines, station, show_plot)


def process_from_file(station: str, show_plot=True):

    station = 'Westminster'
    filename = 'Thames_Levels.html'
    lines = (line for line in tide_data_generator_from_file(filename))

    process(lines, station, show_plot)


if __name__ == "__main__":

    #process_from_file('', show_plot=True)
    #sys.exit(1)

    if False:
        process_from_web('Chelsea')
    else:
        for station in STATIONS:
            process_from_web(station, show_plot=False)
