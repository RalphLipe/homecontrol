import argparse
import scenes
import threading

from scenes import save_scenes, save_shades
from __init__ import Home, save_config


import logging
logger = logging.getLogger(__name__)


def ui_thread_proc(house):
    in_val = ""
    while in_val != "Q" and in_val != "R":
        in_val = input("Enter 'Q' to quit or 'R' to reboot")
        in_val = in_val.upper()
    exit_code = 0 if in_val == "Q" else 255
    house.shut_down(exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = "Control the Lipe Bellevue Home"
    # parser.usage = ""
    parser.add_argument('-config', type=str, help="Name of a configuration file")
    parser.add_argument('-saveconfig', type=str, help="File name to write default configuration parameters to")
    parser.add_argument('-printscenes', action='store_true', help="Print out a list of scenes for lights and shades")
    parser.add_argument('-savescenes', type=str, help="File name to write scene json to")
    parser.add_argument('-saveshades', type=str, help="File name to write shades json to")
    args = parser.parse_args()

    if args.printscenes:
        scenes.print_automation_parameters()

    if args.saveconfig:
        save_config(args.saveconfig)

    if args.savescenes:
        save_scenes(args.savescenes)

    if args.saveshades:
        save_shades(args.saveshades)

    if args.printscenes or args.saveconfig or args.savescenes or args.saveshades:
        quit(0)

    house = Home(args.config)

    ui_thread = threading.Thread(target=lambda: ui_thread_proc(house), daemon=True)
    ui_thread.start()

    exit_code = house.wait_for_shut_down()
    logger.info("Exiting with code %i", exit_code)

    exit(exit_code)
