#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import glob
import os
import sys
import threading
import xml.etree.ElementTree as ET

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import argparse
import time

red = carla.Color(255, 0, 0)
green = carla.Color(0, 255, 0)
cyan = carla.Color(0, 255, 255)
orange = carla.Color(255, 130, 0)
blue = carla.Color(0, 0, 255)
yellow = carla.Color(255, 255, 0)
white = carla.Color(255, 255, 255)

colors = [red, green, orange, cyan, yellow, blue, white]
waypoint_separation = 4


def draw_waypoint_union(debug, l0, l1, color=carla.Color(255, 0, 0), lt=5, draw_point=False, thickness=1.0):
    debug.draw_line(
        l0 + carla.Location(z=0.25),
        l1 + carla.Location(z=0.25),
        thickness=thickness, color=color, life_time=lt, persistent_lines=False)
    if draw_point:
        debug.draw_point(l0 + carla.Location(z=0.25), 0.1, color, lt, False)


def set_attrib(node, key, default):
    """
    Parse XML key for a given node
    If key does not exist, use default value
    """
    return node.attrib[key] if key in node.attrib else default


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    # argparser.add_argument(
    #     '-s', '--seed',
    #     metavar='S',
    #     default=os.getpid(),
    #     type=int,
    #     help='Seed for the random path (default: program pid)')
    argparser.add_argument(
        '--color',
        metavar='C',
        default='green',
        help='Set the color for the path')
    argparser.add_argument(
        '--xml',
        metavar='x',
        default=None,
        help='Set the XML file with the path')
    argparser.add_argument(
        '-lt', '--lifetime',
        metavar='l',
        default=60,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-t', '--tick-time',
        metavar='T',
        default=0.01,
        type=float,
        help='Tick time between updates (forward velocity) (default: 0.1)')
    args = argparser.parse_args()

    # try:
    client = carla.Client(args.host, args.port)
    client.set_timeout(2.0)

    world = client.get_world()
    debug = world.debug

    if args.xml is None:
        raise Exception("No xml with route passed as argument!")
    waypoints_file = args.xml
    if not os.path.isfile(waypoints_file):
        raise Exception(" there is no such an XML file!")
    tree = ET.parse(waypoints_file)

    color = 0

    for routes in tree.iter("routes"):
        for route in routes.iter("route"):
            if color == 0:
                args.lifetime = 20
            else:
                args.lifetime = 15
            threading.Thread(target=draw, args=(route, colors[color % len(colors)], debug, args)).start()
            color += 1

    #finally:
     #   pass


def draw(route, selected_color, debug, args):
    lifetime = args.lifetime
    waypoints_list = []
    for waypoint in route.iter("waypoint"):
        pos_x = float(set_attrib(waypoint, 'x', 0))
        pos_y = float(set_attrib(waypoint, 'y', 0))
        pos_z = float(set_attrib(waypoint, 'z', 0))
        location  = carla.Location(x=pos_x, y=pos_y, z=pos_z)
        waypoints_list.append(location)

    if len(waypoints_list) % 2 != 0:
        waypoints_list.append(location)

    delta = 0
    for idx in range(len(waypoints_list)-1):
        current_w = waypoints_list[idx]
        next_w    = waypoints_list[idx+1]

        draw_waypoint_union(debug, current_w, next_w, selected_color, lifetime-(0.05*delta))
        delta += 1
        time.sleep(args.tick_time)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nExit by user.')
    except Exception as err:
        print(err)
    finally:
        print('\nExit.')