#!/usr/bin/env python3


'''
Save Thames level at a couple of stations of interest

@author:     Adrian Rosoga

@copyright:
'''

__all__ = []
__version__ = 0.1
__date__ = '2020-03-16'
__updated__ = '2020-03-18'


import sys
import datetime
import argparse
import json
from mongoengine import *
from collections import OrderedDict
from tides import tide_data_generator_from_web, TIDE_INFO_WEBPAGE_TEMPLATE, STATIONS


MONGO_DB_TIDES_PREFIX = "tides"


class Measurement(Document):
    timestamp = DateTimeField(required=True)
    level = DecimalField(required=True)
    

def default(obj):
    """ Convert to isoformat - TBC"""

    if isinstance(obj, datetime.datetime):
        return {'_isoformat': obj.isoformat()}
    return super().default(obj)


def object_hook(obj):
    """ Convert from isoformat - TBC"""

    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        return datetime.datetime.fromisoformat(_isoformat)
    return obj


def get_time_series(station):
    """ Process the station"""

    tide_info_page = TIDE_INFO_WEBPAGE_TEMPLATE.format(station=STATIONS[station][0])

    date2level = OrderedDict()

    for date_time, level in tide_data_generator_from_web(tide_info_page):
        date2level[str(date_time)] = level, station

    return date2level


def save_to_mongodb(station, date2level):

    connect(MONGO_DB_TIDES_PREFIX + '_' + station, host='localhost', port=27017)

    for timestamp, level in date2level.items():

        measurement = Measurement(timestamp=timestamp, level=level[0])
        print(timestamp, level[0])
        measurement.save()


def save_to_file(station, date2level):

    last_date = next(reversed(date2level.keys()))
    last_date = str(last_date).replace(':', '-').replace(' ', '_')

    dump_filename = f'Thames_Tide_{station}_{last_date}.dat'
    with open(dump_filename, 'w') as handle:
        json.dump(date2level, handle, indent=4)

    # print(json.dumps(date2level, default=default, indent=4))

    print(f'Data saved into "{dump_filename}"')


def process(station):

    date2level = get_time_series(station)

    save_to_file(station, date2level)
    #save_to_mongodb(station, date2level)


def main():
    """ Main - to please the linter """

    parser = argparse.ArgumentParser(description='Find time between high tides at two stations.\nDefault stations are Chelsea and Dover.')
    parser.add_argument('--list', help='list all stations', action='store_true')
    parser.add_argument('--station', help='station')
    parser.add_argument('--save', help='save to file', action='store_true')
    args = parser.parse_args()

    if args.list:
        for station in STATIONS:
            print(station)
        sys.exit(0)

    station = args.station

    if station is None:
        station = 'Chelsea'

    
    process('Chelsea')
    process('Westminster')


if __name__ == '__main__':

    main()
