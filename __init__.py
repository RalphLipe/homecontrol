import json

from threading import Event
from persistentstore import PersistentStore
from lights import Lights
from timedevent import TimedEventQueue
from vacationmode import VacationMode
from garagetimer import SceneTimer
from sqsevents import SqsEvents
from somfyrts import SomfyRTS
from somfyrts.serialstub import SerialStub
from radiora.scene import Scene

import logging
logger = logging.getLogger(__name__)


# This configuration is used if no file is specified.  In addition to being the default test configuration, it serves
# as the documentation for the file contents.
DEFAULT_CONFIG = {
    # File name for persistent store
    'persistent_store': 'persistentstore.json',
    # Serial port for lights
    'port_lights': 'TEST',
    # Serial port for shades
    'port_shades': 'TEST',
    # Name of AWS SQS queue for command messages
    'queue_name': 'SimpleFirst.fifo',
    # Maximum age (in seconds) of command messages before they are discarded
    'max_message_age': 90,
    # Number of seconds to delay before shutting off garage lights automatically.  0 disables.
    'garage_delay': 300,
    # Number of seconds to delay before shutting of the stairs down automatically.  0 disables.
    'stairs_delay': 300,
    # TODO:  Add vacation mode stuff here
    'vacation start': 0,
    'vacation end': 0,
    'vacation interval': 30 * 60,

    # Logging levels for modules.  0=NOTSET, 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL
    'logging': {
        '__init__': 10,
        '__main__': 10,
        'garagetimer': 10,
        'lights': 10,
        'sqsevents': 10,
        'timedevent': 10,
        'vacationmode': 10,
    },
}


def load_config(file):
    with open(file, 'r') as config_file:
        config = json.load(config_file)
    return config


def save_config(file, config=DEFAULT_CONFIG):
    with open(file, 'w') as config_file:
        json.dump(config, config_file, indent=4)


class Home:
    def __init__(self, file=None):
        self.running = True
        self.exit_code = 0
        self.shut_down_event = Event()

        self.scene_timers = {}

        if file:
            config = load_config(file)
        else:
            config = DEFAULT_CONFIG

        for logger_name, level in config['logging'].items():
            module_logger = logging.getLogger(logger_name)
            console = logging.StreamHandler()
            console.setLevel(level)
            module_logger.setLevel(level)
            module_logger.addHandler(console)
            # TODO:  Add ability to log to different files, etc...

        self.persistent_store = PersistentStore(config['persistent_store'])

        self.timed_event_queue = TimedEventQueue()
        # TODO:  More vacation mode options in config.
        self.vacation_mode = VacationMode(self)
        self.garage_timer_delay = config['garage_delay']
        self.stairs_timer_delay = config['stairs_delay']

        port_lights = config['port_lights']
        if port_lights == "TEST":
            logger.info("Using serial stub for lights (test mode)")
            port_lights = SerialStub()

        port_shades = config['port_shades']
        if port_shades == "TEST":
            logger.info("Using serial stub for shades (test mode)")
            port_shades = SerialStub()

        # It is important to initialize these three services in this order.  The shades are used by Lights and
        # SqsEvents.  Lights are used by SqsEvents.
        self.shades = SomfyRTS(port_shades, thread=True)
        self.lights = Lights(self, port_lights)
        self.sqs_events = SqsEvents(self, config['queue_name'], config['max_message_age'])

        # Now make sure vacation mode is re-enabled if it is currenly on in the persistent store (power failed)
        self.vacation_mode.init_from_persistent_store()

    def __enter__(self):
        """Performs no function.  Returns original object (self)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Calls self.stop() to shut down all threads"""
        self.stop()

    def get_scene_timer(self, scene: Scene) -> SceneTimer:
        if scene in self.scene_timers:
            timer = self.scene_timers[scene]
        else:
            timer = SceneTimer(self, scene)
            self.scene_timers[scene] = timer
        return timer

    def stop(self):
        logger.info("Stopping house services")
        self.running = False

        self.timed_event_queue.stop()
        self.sqs_events.stop()
        self.lights.stop()
        self.shades.close()

    def shut_down(self, exit_code=0):
        self.exit_code = exit.code = exit_code
        self.shut_down_event.set()

    def wait_for_shut_down(self):
        self.shut_down_event.wait()
        self.stop()
        return self.exit_code
