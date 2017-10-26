import threading
import boto3
import json
from datetime import datetime
from scenes import ALEXA_SCENES, SHADES_DICTIONARY


import logging
logger = logging.getLogger(__name__)


class SqsEvents:
    def __init__(self, home, queue_name):
        self._thread = threading.Thread(target=lambda: self._thread_poll_event_queue(queue_name))
        self.continue_running = True
        self.home = home
        self._thread.start()

    def stop(self):
        self.continue_running = False
        self._thread.join()

    def _thread_poll_event_queue(self, queue_name):
        sqs = boto3.resource('sqs')
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        while self.continue_running:
            messages = queue.receive_messages(WaitTimeSeconds=20, AttributeNames=['SentTimestamp'])
            for msg in messages:
                logger.info("Event {0}".format(msg.body))
                epoch_ms = int(msg.attributes['SentTimestamp'])
                msg_time = datetime.fromtimestamp(epoch_ms / 1000)
                msg_age = datetime.now() - msg_time
                if msg_age.total_seconds() > 120:   # TODO - make configurable...
                    logger.info("Throwing away event because it was sent {0} seconds ago".format(msg_age))
                else:
                    event = json.loads(msg.body)
                    if 'event_type' in event:
                        if event['event_type'] == 'change_lights':
                            self._do_light_event(event)
                        elif event['event_type'] == 'change_shades':
                            self._do_shade_event(event)
                        else:
                            logger.debug("Unable to parse parameters for event")  # TODO: MORE AND BETTER ERRORS!!
                msg.delete()

    def _do_light_event(self, event):
        action = event['light_action']
        scene_name = event['scene']
        if scene_name in ALEXA_SCENES:
            scene = ALEXA_SCENES[scene_name]
           # logger.info("Turning {0} {1}".format(scene, action))
            print("Turning {0} {1}".format(scene, action))

            if action == "on":
                scene.on(self.home.lights)
            elif action == "off":
                scene.off(self.home.lights)
            elif action == "dim":
                scene.dim(self.home.lights)
            else:
                logger.debug("Unknown action for light event")
        else:
            logger.debug("Unknown scene for light event.")

    def _do_shade_event(self, event):
        action = event['shade_action']
        room = event['room']
        if room in SHADES_DICTIONARY:
            shade = SHADES_DICTIONARY[room]
            logger.info("Moving shade {0} {1}".format(shade, action))
            # always send commands twice because sometimes they signal is missed
            if action == "raise" or action == "open":
                self.home.shades.up(shade)
                self.home.shades.up(shade)
            elif action == "lower" or action == "close":
                self.home.shades.down(shade)
                self.home.shades.down(shade)
            else:
                logger.debug("Unknown action for light event")
        else:
            logger.debug("Unknown room {0} for light event.".format(room))
