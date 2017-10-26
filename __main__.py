import argparse
import scenes


from __init__ import Home
from somfyrts.serialstub import SerialStub


import logging
logger = logging.getLogger(__name__)

DEFAULT_LIGHTS_PORT = "/dev/cu.usbserial"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = "Control the Lipe Bellevue Home"
    # parser.usage = ""
    parser.add_argument('-lights', type=str, default="/dev/cu.usbserial",
                        help="Port name for RadioRA Chronos system or 'TEST'")
    parser.add_argument('-shades', type=str, default="TEST",
                        help="Port name for Somfy RTS controller or 'TEST'")
    parser.add_argument('-verbose', action='store_true', help="verbose output")
    parser.add_argument('-sqs', type=str, default="SimpleFirst.fifo", help="Queue name for Amazon SQS (Alexa")
    parser.add_argument('-printscenes', action='store_true', help="Print out a list of scenes for lights and shades")
    parser.epilog = "If -lights is specified, -shades must be also."
    args = parser.parse_args()

    if args.printscenes:
        scenes.print_automation_parameters()
        quit(0)   # TODO: Perhaps move this to some tool utility thing...

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    port_lights = args.lights
    if port_lights == "TEST":
        port_lights = SerialStub()

    port_shades = args.shades
    if port_shades == "TEST":
        port_shades = SerialStub()

    house = Home(port_lights, port_shades, args.sqs)

    input("Press enter to quit")

    print("Stopping the house process.  This can take up to 20 seconds.")
    house.stop()
