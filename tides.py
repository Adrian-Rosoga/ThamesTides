import re
import datetime
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot
import matplotlib.dates as mdates
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#
# Adrian Rosoga, 19 Jan 2020
#
# Westminster
# https://flood-warning-information.service.gov.uk/station/7389?direction=u#summary-express
# Chelsea
# https://flood-warning-information.service.gov.uk/station/7392?direction=u#summary-express
#
# <tr>
#     <td scope="row"><time datetime="2020-01-14T17:15Z">2020-01-14T17:15Z</time></td>
#     <td class="numeric">3.622</td>
#     <td>false</td>
# </tr>


tide_info_page_westminster = 'https://flood-warning-information.service.gov.uk/station/7389?direction=u#summary-express'
tide_info_page_chelsea = 'https://flood-warning-information.service.gov.uk/station/7392?direction=u#summary-express'

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

    vertical_water_speed_cm_per_min = [(l2 - l1) * 100.0 / 15.0 for l2, l1 in zip(levels[1:], levels[:-1])]

    #for date, level, speed in zip(dates, levels, vertical_water_speed_cm_per_min):
    #    print(f"{date}: Level={level:5.2f} m   Rise={speed:5.2f} cm/min")

    print("")
    print(f'=== {station}')
    #print(f"{len(date_levels)} water levels")
    print(f"Maximum level {max(levels)} m")
    print(f"Minimum level {min(levels)} m")
    print(f"Delta {max(levels) - min(levels):.1f} m")
    print(f"Maximum vertical speed {max(vertical_water_speed_cm_per_min):.2f} cm per min")
    print(f"Minimum vertical speed {min(vertical_water_speed_cm_per_min):.2f} cm per min")
    # print(f"{len(levels)} levels recorded, {len(set(levels))} unique ones")
    # print(f"{len(vertical_water_speed_cm_per_min)} water speed recorded, {len(set(vertical_water_speed_cm_per_min))} unique ones")
    print(f"From {date_levels[0][0]} to {date_levels[len(date_levels) - 1][0]}")

    figure = matplotlib.pyplot.figure()
    plot = figure.add_subplot(111)

    plot.plot(dates, levels, 'blue', marker="*")

    matplotlib.pyplot.ylabel("Water level (m)", color='blue', fontweight='bold', fontsize='17')

    # plot.plot(dates, levels, marker=matplotlib.markers.CARETDOWNBASE)
    #plot.plot(dates, levels, marker=".")
    plot2 = plot.twinx()

    plot2.plot(dates[:-1], vertical_water_speed_cm_per_min, 'orange', marker=".", linewidth=0.5)

    sns.set(style='ticks')

    plot.axhline(linewidth=1, color='r')
    plot.grid(color='g', linestyle=':', linewidth=0.5)

    matplotlib.pyplot.xlabel("Date")
    #matplotlib.pyplot.ylabel("Water level (m) and tide rise speed (cm/min)")

    plot.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    plot2.format_xdata = mdates.DateFormatter('%Y-%m-%d')

    plot.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    plot2.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    matplotlib.pyplot.ylabel("Tide rise speed (cm/min)", color='orange', fontweight='bold', fontsize='17')

    font = {'family': 'serif',
            'color': 'darkred',
            'weight': 'bold',
            'size': 16, }

    plot.scatter(dates[-1], levels[-1], marker=m)
    plot2.scatter(dates[-2], vertical_water_speed_cm_per_min[-1], marker=m)

    matplotlib.pyplot.title(f'Thames at {station} (2 days)\n{dates[-1]}', fontdict=font)

    # DOES NOT WORK FOR 2 PLOTS matplotlib.pyplot.xticks(rotation=45)

    for label in plot.get_xticklabels() + plot2.get_xticklabels():
        label.set_rotation(30)
        label.set_ha('right')

    t = matplotlib.pyplot.text(dates[0], 0, f'min={min(levels):.1f}m max={max(levels):.1f} delta={(max(levels) - min(levels)):.1f}m')
    t.set_bbox(dict(facecolor='yellow', alpha=1, edgecolor='blue'))

    last_date = str(dates[-1]).replace(' ', '_')
    last_date = last_date.replace(':', '-')
    #matplotlib.pyplot.figure(figsize=(6.4, 6.4), dpi=200)
    matplotlib.pyplot.savefig(f'records/Thames_at_{station}_{last_date}.png', dpi=300)

    if show_plot:
        matplotlib.pyplot.show()


def main(station: str, show_plot=True):

    tide_info_page = tide_info_webpage_template.format(station=STATIONS[station])
    lines = (line for line in tide_data_generator_from_web(tide_info_page))

    #station = 'Westminster'
    #filename = 'Thames_Levels.html'
    #lines = (line for line in tide_data_generator_from_file(filename))

    process(lines, station, show_plot)


if __name__ == "__main__":

    if True:
        main('Chelsea')
    else:
        for station in STATIONS:
            main(station, False)
