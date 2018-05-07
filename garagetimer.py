from timedevent import TimedEvent
from datetime import datetime, timedelta
from radiora.scene import Scene


import logging
logger = logging.getLogger(__name__)


class SceneTimedEvent(TimedEvent):
    def __init__(self, home, scene: Scene, delay: timedelta):
        TimedEvent.__init__(self, datetime.now() + delay, event_id=scene)
        self.home = home
        self.scene = scene

    def execute(self):
        logger.info("Light timer turning off %s", self.scene)
        self.scene.off(self.home.lights)


class SceneTimer:
    def __init__(self, home, scene: Scene):
        self.home = home
        self.scene = scene

    def reset_and_start(self, delay_seconds: int):
        self.stop()
        if delay_seconds > 0:
            logger.info("Starting %s timer for %i seconds", self.scene, delay_seconds)
            self.home.timed_event_queue.add_event(
                SceneTimedEvent(self.home, self.scene, timedelta(seconds=delay_seconds)))
        else:
            logger.info("Timer %s not started because 0 second delay (disabled in current configuration?)", self.scene)

    def stop(self):
        logger.info("Stopping %s timer", self.scene)
        self.home.timed_event_queue.remove_events(SceneTimedEvent, event_id=self.scene)


