import re
import sys
import datetime
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#
# Adrian Rosoga, 19 Jan 2020
#
# Westminster: https://flood-warning-information.service.gov.uk/station/7389
#
# <tr>
#     <td scope="row"><time datetime="2020-01-14T17:15Z">2020-01-14T17:15Z</time></td>
#     <td class="numeric">3.622</td>
#     <td>false</td>
# </tr>


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
    print(f"Maximum level {max(levels)} m"
          f"Minimum level {min(levels)} m")
    print(f"Delta {max(levels) - min(levels):.1f} m")
    print(f"Maximum vertical speed {max(tide_speed_cm_per_min):.2f} cm per min")
    print(f"Minimum vertical speed {min(tide_speed_cm_per_min):.2f} cm per min")
    print(f"From {date_levels[0][0]} to {date_levels[len(date_levels) - 1][0]}")

    plot(station, dates, levels, tide_speed_cm_per_min, show_plot)


def plot(station, dates, levels, tide_speed_cm_per_min, show_plot):

    # Colors from http://ksrowell.com/blog-visualizing-data/2012/02/02/optimal-colors-for-graphs/
    water_color = '#396AB1'
    tide_rise_color = '#DA7C30'
    title_color = '#535154'
    box_background_color = '#CCC210'

    station_description = STATIONS[station][1]

    figure = plt.figure(figsize=(20, 10))
    plot = figure.add_subplot(111)

    plot.plot(dates, levels, water_color, marker="*", label="Water level")

    plt.ylabel("Water level (m)", color=water_color, fontweight='bold', fontsize=17)

    plot2 = plot.twinx()

    plot2.plot(dates[:-1], tide_speed_cm_per_min, tide_rise_color, marker=".", linewidth=0.5, label="Tide rise speed")

    # Grid
    plot.axhline(linewidth=1, color='r')
    plot.grid(color='g', linestyle=':', linewidth=0.5)

    plt.xlabel("Date")

    plot.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plot2.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')

    plt.ylabel("Tide rise speed (cm/min)", color=tide_rise_color, fontweight='bold', fontsize=17)

    # Mark the last point on each graph
    plot.scatter(dates[-1], levels[-1], marker='s', s=400, c=water_color)
    plot2.scatter(dates[-2], tide_speed_cm_per_min[-1], marker='s', s=400, c=tide_rise_color)

    title_font = {'family': 'serif',
                  'color': title_color,
                  'weight': 'bold',
                  'size': 24, }

    # Title
    plt.title(f'{station_description} (2 days)\n{dates[-1]}', fontdict=title_font)

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
                              f'Current={levels[-1]:.1f}m\nMin={min(levels):.1f}m Max={max(levels):.1f} Delta={(max(levels) - min(levels)):.1f}m',
                              fontsize=32)
    level_info_box.set_bbox(dict(facecolor=box_background_color, alpha=1, edgecolor=box_background_color))

    # Legend
    plot.legend(loc='upper left', fontsize='x-large')
    plot2.legend(loc='upper right', fontsize='x-large')

    # Save to file
    last_date = str(dates[-1]).replace(' ', '_').replace(':', '-')
    plt.savefig(f'records/{station_description}_{last_date}.png', dpi=300)

    if show_plot:
        plt.show()


def process_from_web(station: str, show_plot=True):

    tide_info_page = tide_info_webpage_template.format(station=STATIONS[station][0])
    lines = (line for line in tide_data_generator_from_web(tide_info_page))

    process(lines, station, show_plot)


def process_from_file(station: str, show_plot=True):

    station = 'Westminster'
    filename = 'test/Thames_Tide.html'
    lines = (line for line in tide_data_generator_from_file(filename))

    process(lines, station, show_plot)


if __name__ == "__main__":

    process_from_file('', show_plot=True)

    #process_from_web('Chelsea')
    #process_from_web('Dover')

    sys.exit(1)

    if False:
        process_from_web('Chelsea')
    else:
        for station in STATIONS:
            process_from_web(station, show_plot=False)
