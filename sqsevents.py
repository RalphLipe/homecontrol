import threading
import boto3
import json
from datetime import datetime, timedelta
from scenes import ALL_SCENES, SHADES_DICTIONARY


import logging
logger = logging.getLogger(__name__)


class SqsEvents:
    def __init__(self, home, queue_name: str, max_message_age: int):
        self.home = home
        self.continue_running = True
        self.queue_name = queue_name
        self.max_message_age = timedelta(seconds=max_message_age)
        self._thread = threading.Thread(target=lambda: self._thread_poll_event_queue(queue_name))
        self._thread.start()

    def stop(self):
        logger.info("Stopping SqsEvents service.  This can take up to 20 seconds")
        self.continue_running = False
        self._thread.join()

    def _thread_poll_event_queue(self, queue_name):
        try:
            sqs = boto3.resource('sqs')
            queue = sqs.get_queue_by_name(QueueName=queue_name)
            logger.info("Opened SQS queue %s", queue_name)
            while self.continue_running:
                messages = queue.receive_messages(WaitTimeSeconds=20, AttributeNames=['SentTimestamp'])
                for msg in messages:
                    logger.info("Event {0}".format(msg.body))
                    epoch_ms = int(msg.attributes['SentTimestamp'])
                    msg_time = datetime.fromtimestamp(epoch_ms / 1000)
                    msg_age = datetime.now() - msg_time
                    if msg_age > self.max_message_age:
                        logger.info("Discarding event because it was sent {0} seconds ago".format(msg_age.total_seconds()))
                    else:
                        event = json.loads(msg.body)
                        if 'event_type' in event:
                            if event['event_type'] == 'change_lights':
                                self._do_light_event(event)
                            elif event['event_type'] == 'change_shades':
                                self._do_shade_event(event)
                            elif event['event_type'] == 'reboot':
                                self.home.shut_down(255)
                            else:
                                logger.error("Unable to parse parameters for event")
                    msg.delete()
        except Exception as inst:
            print("Exception during queue event servicing {0}".format(inst))
            self.home.shut_down(255)

    def _do_light_event(self, event):
        action = event['light_action']
        scene_name = event['scene']
        if scene_name in ALL_SCENES:
            scene = ALL_SCENES[scene_name]
            logger.info("Turning {0} {1}".format(scene, action))
            if action == "on":
                scene.on(self.home.lights)
            elif action == "off":
                scene.off(self.home.lights)
            elif action == "dim":
                scene.dim(self.home.lights)
            else:
                logger.error("Unknown action '{0}' for light event".format(action))
        else:
            logger.error("Unknown scene '{0}' for light event.".format(scene_name))

    # Although the Alexa grammar allows for words other than 'open' and 'close' all the spoken commands are normalized
    # into just 'open' or 'close'.  'stop' is not currently supported by the Alexa function, but it is supported here.
    def _do_shade_event(self, event):
        action = event['shade_action']
        room = event['room']
        if room in SHADES_DICTIONARY:
            shade = SHADES_DICTIONARY[room]
            logger.info("Moving shade {0} {1}".format(shade, action))
            # Send the same command 4 times because the signal is sometimes missed.
            if not isinstance(shade, list):
                shade = [shade]
            shade *= 4
            if action == "open":
                self.home.shades.up(shade)
            elif action == "close":
                self.home.shades.down(shade)
            elif action == "stop":
                self.home.shades.stop(shade)
            else:
                logger.error("Unknown action for light event")
        else:
            logger.error("Unknown room {0} for light event.".format(room))
