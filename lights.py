from radiora import RadioRA, RaiseButtonPress, LowerButtonPress, MasterControlButtonPress, LocalZoneChange, STATE_OFF
from scenes import ZONES, MASTER_CONTROLS, SHADES_ALL


# Magic things:
# * When vacation is pressed then vacation lighting mode turns on.  Vacation lighting mode randomly turns on and off
#   different zones within a specified time range (sunset to midnight is the default).  There is a five minute pause
#   before the lighting rotation begins.
# * Vacation lighting mode is turned off when any button is pressed EXCEPT leave, vacation (other magic happens) or
#   the switch in the garage is pressed (garage lights don't turn vacation or leave off)
# * Five minutes after pressing vacation, vacation mode begins, and the garage light is turned off
# * Five minutes after pressing leave, the garage light is turned off
# * When either leave or vacation is pressed twice (once the LED has become solid) all the shades will be closed.
# * When the "UP" button in the bedroom is pressed the master lights turn on full
# * When the "DOWN" button is pressed in the master the lights are set to dim
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
        garage = MASTER_CONTROLS['garage']
        if feedback.master_control_number == garage.master_control_number:
            self.home.garage_light_timer.reset_and_start()
            button_name = garage.buttons[feedback.button_number]
            if button_name == 'vacation':
                self.home.vacation_mode.enable()
            else:
                self.home.vacation_mode.disable()
            if button_name in ('leave', 'vacation') and feedback.state == STATE_OFF:
                # do the command twice because sometimes the signal is missed
                self.home.shades.down(SHADES_ALL)
                self.home.shades.down(SHADES_ALL)
        else:
            self.home.vacation_mode.disable()

    def _local_zone_change(self, feedback: LocalZoneChange):
        if ZONES['garage'].zone_number != feedback.zone_number:
            self.home.vacation_mode.disable()

    def _raise_button_press(self, feedback: RaiseButtonPress):
        if MASTER_CONTROLS['master bedroom'].master_control_number == feedback.master_control_number:
            ZONES['master bedroom'].on(self)

    def _lower_button_press(self, feedback: RaiseButtonPress):
        if MASTER_CONTROLS['master bedroom'].master_control_number == feedback.master_control_number:
            ZONES['master bedroom'].dim(self)
