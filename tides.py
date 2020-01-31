import re
import datetime
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot
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


def tide_data_generator(tide_info_page: str):

    page = requests.get(tide_info_page)

    if page.status_code != requests.codes.ok:
        print('Error')
        raise StopIteration

    # TODO - Extract only relevant info
    # soup = BeautifulSoup(page.text, 'html.parser')
    # items = soup.find_all('tr')

    for line in page.text.split('\n'):
        yield line


def main(tide_info_page: str):

    lines = (line for line in tide_data_generator(tide_info_page))

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

    for date, level, speed in zip(dates, levels, vertical_water_speed_cm_per_min):
        print(f"{date}: Level={level:5.2f} m   Rise={speed:5.2f} cm/min")

    print("")
    print(f"{len(date_levels)} water levels")
    print(f"Maximum level {max(levels)} m")
    print(f"Minimum level {min(levels)} m")
    print(f"Maximum vertical speed {max(vertical_water_speed_cm_per_min):.2f} cm per min")
    print(f"Minimum vertical speed {min(vertical_water_speed_cm_per_min):.2f} cm per min")
    # print(f"{len(levels)} levels recorded, {len(set(levels))} unique ones")
    # print(f"{len(vertical_water_speed_cm_per_min)} water speed recorded, {len(set(vertical_water_speed_cm_per_min))} unique ones")
    print(f"From {date_levels[0][0]} to {date_levels[len(date_levels) - 1][0]}")

    figure = matplotlib.pyplot.figure()
    plot = figure.add_subplot(111)

    plot.plot(dates, levels, 'blue', marker=".")

    matplotlib.pyplot.ylabel("Water level (m)",  color='blue', fontweight='bold', fontsize='17')

    # plot.plot(dates, levels, marker=matplotlib.markers.CARETDOWNBASE)
    #plot.plot(dates, levels, marker=".")
    plot2 = plot.twinx()

    plot2.plot(dates[:-1], vertical_water_speed_cm_per_min, 'orange', marker=".")

    sns.set(style='ticks')

    plot.axhline(linewidth=1, color='r')
    plot.grid(color='g', linestyle=':', linewidth=0.5)

    matplotlib.pyplot.xlabel("Date")
    #matplotlib.pyplot.ylabel("Water level (m) and vertical tide speed (cm/min)")

    matplotlib.pyplot.ylabel("Tide rise speed (cm/min)", color='orange', fontweight='bold', fontsize='17')

    matplotlib.pyplot.show()


if __name__ == "__main__":

    #main(tide_info_page_westminster)
    main(tide_info_page_chelsea)
