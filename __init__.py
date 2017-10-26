from lights import Lights
from timedevent import TimedEventQueue
from vacationmode import VacationMode
from garagetimer import GarageTimer
from sqsevents import SqsEvents
from somfyrts import SomfyRTS


class Home:
    def __init__(self, port_lights, port_shades, sqs_queue_name):
        self.running = True

        self.timed_event_queue = TimedEventQueue()
        self.vacation_mode = VacationMode(self)  # interval=timedelta(seconds=20))  # *** TEST VACATION
        self.garage_light_timer = GarageTimer(self)

        self.shades = SomfyRTS(port_shades, thread=True)    # Shades don't use lights or external events
        self.lights = Lights(self, port_lights)             # Lights use shades (leave & vacation buttons)
        self.sqs_events = SqsEvents(self, sqs_queue_name)   # External events use everything
        # **** TEST VACATION!!!
        # *** UNDO THIS AND DO MORE TESTS self.vacation_mode.enable(delay=timedelta(seconds=10))

    def __enter__(self):
        """Performs no function.  Returns original object (self)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Calls self.stop() to shut down all threads"""
        self.stop()

    def stop(self):
        self.running = False

        self.timed_event_queue.stop()
        self.sqs_events.stop()
        self.lights.stop()
        self.shades.close()
