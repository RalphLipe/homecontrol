from timedevent import TimedEvent
from scenes import ZONES
from datetime import datetime, timedelta


class GarageTimer:
    class GarageTimedEvent(TimedEvent):
        def __init__(self, event_time, home):
            TimedEvent.__init__(self, event_time)
            self.home = home

        def execute(self):
            ZONES['garage'].off(self.home.lights)

    def __init__(self, home, delay=timedelta(minutes=5)):
        self.home = home
        self.delay = delay

    def reset_and_start(self):
        self.stop()
        self.home.timed_event_queue.add_event(self.GarageTimedEvent(datetime.now() + self.delay, self.home))

    def stop(self):
        self.home.timed_event_queue.remove_events(self.GarageTimedEvent)
