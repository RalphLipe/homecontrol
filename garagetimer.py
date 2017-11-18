from timedevent import TimedEvent
from datetime import datetime, timedelta
from radiora.scene import Scene
from scenes import ZONES, VIRTUAL_SCENES


import logging
logger = logging.getLogger(__name__)


class LightTimedEvent(TimedEvent):
    def __init__(self, light_timer):
        TimedEvent.__init__(self, datetime.now() + light_timer.delay)
        self.light_timer = light_timer

    def execute(self):
        logger.info("Light timer turning off %s", self.light_timer.zone)
        self.light_timer.zone.off(self.light_timer.home.lights)


class LightTimer:
    def __init__(self, home, delay: int, zone: Scene, light_event_class):
        self.home = home
        self.delay = timedelta(seconds=delay)
        self.zone = zone
        self.light_event_class = light_event_class

    def reset_and_start(self):
        self.stop()
        if self.delay.total_seconds() > 0:
            logger.info("Starting %s timer", self.zone)
            self.home.timed_event_queue.add_event(self.light_event_class(self))
        else:
            logger.info("Timer %s not started because it is disabled in the current configuration", self.zone)

    def stop(self):
        logger.info("Stopping %s timer", self.zone)
        self.home.timed_event_queue.remove_events(self.light_event_class)


class GarageTimer(LightTimer):
    class GarageTimedEvent(LightTimedEvent):
        pass

    def __init__(self, home, delay: timedelta):
        LightTimer.__init__(self, home, delay, ZONES['garage'], self.GarageTimedEvent)


class StairsTimer(LightTimer):
    class StairsTimedEvent(LightTimedEvent):
        pass

    def __init__(self, home, delay: timedelta):
        LightTimer.__init__(self, home, delay, VIRTUAL_SCENES['stairs down'], self.StairsTimedEvent)
