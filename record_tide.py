#!/usr/bin/env python3

import sys
import datetime
import argparse
import json
from collections import OrderedDict
from tides import tide_data_generator_from_web, parse, TIDE_INFO_WEBPAGE_TEMPLATE, STATIONS


def default(obj):
    if isinstance(obj, datetime.datetime):
        return { '_isoformat': obj.isoformat() }
    return super().default(obj)


def object_hook(obj):
    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        return datetime.fromisoformat(_isoformat)
    return obj


def process(station):

    tide_info_page = TIDE_INFO_WEBPAGE_TEMPLATE.format(station=STATIONS[station][0])

    date2level = OrderedDict()

    for k, v in tide_data_generator_from_web(tide_info_page):
        date2level[str(k)] = v, station

    last_date = next(reversed(date2level.keys()))
    last_date = str(last_date).replace(':', '-').replace(' ', '_')

    dump_filename = f'Thames_Tide_{station}_{last_date}.dat'
    with open(dump_filename, 'w') as fp:
        json.dump(date2level, fp, indent=4)

    print(json.dumps(date2level, default=default, indent=4))

    print(f'Data saved into "{dump_filename}"')


def main():

    parser = argparse.ArgumentParser(description='Find time between high tides at two stations.\nDefault stations are Chelsea and Dover.')
    parser.add_argument('--list', help='list all stations', action='store_true')
    parser.add_argument('--station', help='station')
    parser.add_argument('--save', help='save to file', action='store_true')
    args = parser.parse_args()

    if args.list:
        for station in STATIONS.keys():
            print(station)
        sys.exit(0)

    save_to_file = False if not args.save else True

    station = args.station

    if station is None:
        station = 'Chelsea'

    process('Chelsea')
    process('Westminster')


if __name__ == '__main__':

    main()
