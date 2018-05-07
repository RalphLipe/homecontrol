import threading
import bisect

from datetime import datetime

import logging
logger = logging.getLogger(__name__)


class TimedEvent:
    def __init__(self, event_time, event_id: object = None):
        self.event_time = event_time
        self.event_id = event_id

    def __lt__(self, other):
        if isinstance(other, TimedEvent):
            return self.event_time < other.event_time
        if isinstance(other, datetime):
            return self.event_time < other
        raise TypeError("Can not compare other to TimedEvent")

    def execute(self):
        assert False


class TimedEventQueue:
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
        self._check_event_queue = threading.Event()
        self._continue_running = True
        self._thread = threading.Thread(target=lambda: self._thread_event_loop())
        self._thread.start()

    def _thread_event_loop(self):
        while self._continue_running:
            with self._lock:
                if len(self._queue) == 0:
                    timeout = None
                else:
                    # make sure the timeout is not negative.
                    timeout = max(0.0, (datetime.now() - self._queue[0].event_time).total_seconds())
            self._check_event_queue.wait(timeout=timeout)
            if self._continue_running:
                with self._lock:
                    event = None
                    if len(self._queue) > 0 and self._queue[0].event_time <= datetime.now():
                        event = self._queue.pop(0)
                    if len(self._queue) == 0 or event is None:
                        self._check_event_queue.clear()
                if event is not None:
                    event.execute()

    def stop(self):
        with self._lock:
            self._continue_running = False
            self._queue = []
            self._check_event_queue.set()
        self._thread.join()

    def add_event(self, event):
        with self._lock:
            bisect.insort(self._queue, event)
            self._check_event_queue.set()

    def remove_events(self, event_class, event_id: object = None):
        with self._lock:
            new_queue = []
            for event in self._queue:
                if (not isinstance(event, event_class)) or event.event_id != event_id:
                    new_queue.append(event)
            self._queue = new_queue
            # Do not need to set the _check_event_queue event because it's not possible to have a shorter timeout now

