from timedevent import TimedEvent
from scenes import ZONES
from datetime import datetime, timedelta


import logging
logger = logging.getLogger(__name__)


class GarageTimedEvent(TimedEvent):
    def __init__(self, event_time, home):
        TimedEvent.__init__(self, event_time)
        self.home = home

    def execute(self):
        logger.info("Garage timer turning off lights")
        ZONES['garage'].off(self.home.lights)


class GarageTimer:
    def __init__(self, home, delay: timedelta):
        self.home = home
        self.delay = delay

    def reset_and_start(self):
        self.stop()
        logger.info("Starting garage timer")
        self.home.timed_event_queue.add_event(GarageTimedEvent(datetime.now() + self.delay, self.home))

    def stop(self):
        logger.info("Stopping garage timer")
        self.home.timed_event_queue.remove_events(GarageTimedEvent)
