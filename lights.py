from radiora import RadioRA, RaiseButtonPress, LowerButtonPress, MasterControlButtonPress, LocalZoneChange, STATE_OFF
from scenes import ZONES, MASTER_CONTROLS, SHADES_ALL, ALL_SCENES


import logging
logger = logging.getLogger(__name__)


#
# Magic things:
# * When vacation is pressed then vacation lighting mode turns on.
# * Vacation lighting mode is turned off when any button except for the garage light switch
# * Five minutes after pressing any button on the garage master control, the garage light is turned off
# * When vacation is pressed twice (once the LED has become solid) all the shades will be closed.
# * When the "UP" button in the bedroom is pressed the master lights turn on full
# * When the "DOWN" button is pressed in the master the lights are set to dim
#
class Lights(RadioRA):
    def __init__(self, home, port):
        RadioRA.__init__(self, port)
        self.home = home

        self.set_feedback_observer(MasterControlButtonPress, lambda f: self._master_control_button_press(f))
        self.set_feedback_observer(LocalZoneChange, lambda f: self._local_zone_change(f))
        self.set_feedback_observer(RaiseButtonPress, lambda f: self._raise_button_press(f))
        self.set_feedback_observer(LowerButtonPress, lambda f: self._lower_button_press(f))
        self.local_zone_change_monitoring(True)
        self.master_control_button_press_monitoring(True)

    def _master_control_button_press(self, feedback: MasterControlButtonPress):
        logger.info("Master control %i, pressed button %i", feedback.master_control_number, feedback.button_number)
        garage = MASTER_CONTROLS['garage']
        if feedback.master_control_number == garage.master_control_number:
            self.home.get_scene_timer(ALL_SCENES['garage']).reset_and_start(self.home.garage_timer_delay)
            if garage.buttons[feedback.button_number] == 'vacation':
                logger.info("Vacation button pressed.  Enabling vacation mode")
                self.home.vacation_mode.enable()
                if feedback.state == STATE_OFF:         # Two presses shuts all the shades
                    logger.info("Vacation button pressed while on - closing shades")
                    self.home.shades.down(SHADES_ALL * 4)   # Do it 4 times because the signal is sometimes missed
            else:
                self.home.vacation_mode.disable()
                if garage.buttons[feedback.button_number] == 'home':
                    self.home.get_scene_timer(ALL_SCENES['stairs up']).reset_and_start(self.home.stairs_timer_delay)
        else:
            self.home.vacation_mode.disable()

    def _local_zone_change(self, feedback: LocalZoneChange):
        zone = ZONES.zone_for_feedback(feedback)
        if zone is None:
            logger.info("Unknown local zone %i changed to %s", feedback.zone_number, feedback.state)
        else:
            logger.info("%s changed to %s", zone, feedback.state)
        if ZONES['garage'].zone_number != feedback.zone_number:
            self.home.vacation_mode.disable()

    def _raise_button_press(self, feedback: RaiseButtonPress):
        if MASTER_CONTROLS['master bedroom'].master_control_number == feedback.master_control_number:
            ZONES['master bedroom'].on(self)

    def _lower_button_press(self, feedback: RaiseButtonPress):
        if MASTER_CONTROLS['master bedroom'].master_control_number == feedback.master_control_number:
            ZONES['master bedroom'].dim(self)
