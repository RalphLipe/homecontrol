import random

from astral import Astral
from datetime import datetime, timedelta, time
from timedevent import TimedEvent
from scenes import VACATION_SCENES


class VacationMode:
    class VacationBuildEvent(TimedEvent):
        def __init__(self, event_time, parent):
            TimedEvent.__init__(self, event_time)
            self.parent = parent

        def execute(self):
            date = datetime.now().date()
            events = self.parent.create_scene_script(date)
            for event in events:
                if event.event_time >= datetime.now():
                    self.parent.home.timed_event_queue.add_event(event)
            date += timedelta(days=1)
            next_build_time = datetime.combine(date, time(10))
            next_build_event = VacationMode.VacationBuildEvent(next_build_time, self.parent)
            self.parent.home.timed_event_queue.add_event(next_build_event)

    class VacationLightEvent(TimedEvent):
        def __init__(self, event_time, home, scene_off, scene_on):
            TimedEvent.__init__(self, event_time)
            self.home = home
            self.scene_off = scene_off
            self.scene_on = scene_on

        def execute(self):
            if self.scene_off is not None:
                print("Vacation turning off {0}".format(self.scene_off.names[0]))
                self.scene_off.off(self.home.lights)
            if self.scene_on is not None:
                print("Vacation turning on {0}".format(self.scene_on.names[0]))
                self.scene_on.on(self.home.lights)

    def __init__(self, home, start=timedelta(minutes=-30), end_time=time(23, 0, 0), interval=timedelta(minutes=30)):
        self.next_vacation_mode_transition = datetime.max
        self.start = start
        self.end_time = end_time
        self.interval = interval
        self.home = home
        self.enabled = False

    def enable(self, delay=timedelta(minutes=5)):
        if not self.enabled:
            self.enabled = True
            self.home.timed_event_queue.add_event(self.VacationBuildEvent(datetime.now() + delay, self))

    def disable(self):
        self.enabled = False
        self.home.timed_event_queue.remove_events(self.VacationBuildEvent)
        self.home.timed_event_queue.remove_events(self.VacationLightEvent)

    # noinspection PyUnusedLocal
    def create_scene_script(self, date):
        if isinstance(self.start, timedelta):
            a = Astral()
            start_time = (a['seattle'].sun(date=date, local=True)['sunset'] + self.start).time()
        else:
            start_time = self.start
        last_on = None
        events = []
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, self.end_time)
        while start_datetime < end_datetime:
            next_on = random.choice(VACATION_SCENES.all_scenes)
            if next_on == last_on:
                next_on = None      # If we randomly choose the same scene twice in a row, don't turn anything on
            events.append(self.VacationLightEvent(start_datetime, self.home, last_on, next_on))
            last_on = next_on
            start_datetime += self.interval
        return events
