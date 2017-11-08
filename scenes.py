from radiora.scene import *


SHADES_FAMILY_ROOM = 1
SHADES_DINING_ENTRY = 2
SHADES_OFFICE = 3
SHADES_MASTER_BED = 4
SHADES_DOWNSTAIRS = 5

SHADES_ALL = [SHADES_FAMILY_ROOM,
              SHADES_DINING_ENTRY,
              SHADES_OFFICE,
              SHADES_MASTER_BED,
              SHADES_DOWNSTAIRS]

SHADES_DICTIONARY = {
    'family room': SHADES_FAMILY_ROOM,
    'living room': SHADES_FAMILY_ROOM,
    'dining': SHADES_DINING_ENTRY,
    'dining room': SHADES_DINING_ENTRY,
    'entry': SHADES_DINING_ENTRY,
    'office': SHADES_OFFICE,
    'bedroom': SHADES_MASTER_BED,
    'master': SHADES_MASTER_BED,
    'master bedroom': SHADES_MASTER_BED,
    'upstairs': SHADES_MASTER_BED,
    'pool room': SHADES_DOWNSTAIRS,
    'downstairs': SHADES_DOWNSTAIRS,
    'all': SHADES_ALL,
    'all the': SHADES_ALL
}


# ------------- RadioRA Zone Assignments


ZONES = SceneGroup((
    # Main Floor
    GrafikEye(['family room', 'living room'], 13, off=0, on=1, dim=2, fireplace_on=3, fireplace_off=4),
    GrafikEye('office', 15, off=0, on=1, dim=2, fireplace_on=3, fireplace_off=4),
    GrafikEye('kitchen', 10, off=0, on=1, dim=2, cans=3, island=4),
    GrafikEye(['nook', 'breakfast nook'], 11,  off=0, on=1, dim=2, desk=3, table=4),
    GrafikEye('backyard', 12, off=0, on=1, patio=2, fireplace_on=3, path_only=4, fireplace_off=6),
    GrafikEye('front door', 9, all_off=0, entry_on=1, entry_dim=2, outside_on=3, outside_off=4, entry_off=15),
    Dimmer(['laundry room', 'laundry'], 25, on_setting=70, dim_setting=30),
    Dimmer(['end of hall', 'end of the hall'], 27),
    Dimmer(['dining room', 'dining'], 30),
    Dimmer('powder lights', 21),
    Dimmer('powder sink', 28),
    Switch('fountain', 20),

    # Upstairs
    GrafikEye('stairs up', 8, off=0, on=1, dim=2, stairs_on=3, stairs_dim=4),
    GrafikEye('master bedroom', 7, off=0, on=1, dim=2, fireplace_on=3, fireplace_off=4),
    GrafikEye('master bathroom', 6, off=0, on=1, dim=2, fan_on=3, fan_off=4),
    Dimmer('packing room', 17),
    Dimmer('nicole bathroom', 29),
    Dimmer('nicole bedroom', 16),
    Dimmer('master toilet', 26),
    Dimmer('master closet', 24, on_setting=70, dim_setting=30),

    # Downstairs
    GrafikEye('basement', 14, off=0, on=1, dim=2, cabinets=3, pendants=4),
    Dimmer('basement cans', 3),
    Dimmer('hall cans', 4),
    Dimmer('hall sconces', 5),
    Dimmer('stair cans', 31),
    Dimmer('stair sconces', 32),
    Dimmer('theater cans', 1),
    Dimmer('theater background', 2),
    Dimmer('bathroom', 23),
    Dimmer('exercise room', 18),
    Dimmer('james bedroom', 19),
    Switch('garage', 22)
    ))

# This scene needs to be declared before VIRTUAL_SCENES because it is used in the composite scene 'stairs'
_STAIRS_DOWN = CompositeScene('stairs down', (ZONES['hall sconces'], ZONES['stair cans'], ZONES['stair sconces']))


VIRTUAL_SCENES = SceneGroup((
    _STAIRS_DOWN,
    CompositeScene('stairs', (_STAIRS_DOWN, ZONES['stairs up'])),
    CompositeScene('powder room', (ZONES['powder lights'], ZONES['powder sink'])),
    CompositeScene('kitchen and nook', (ZONES['kitchen'], ZONES['nook'])),
    CompositeScene('theater', (ZONES['theater cans'], ZONES['theater background'])),
    CompositeScene('master', (ZONES['master bedroom'], ZONES['master bathroom'],
                              ZONES['master closet'], ZONES['master toilet'])),
    PhantomButton('hall', button_on=4, button_off=5),
    PhantomButton(['main', 'main floor'], button_on=8, button_off=9, button_dim=14),
    PhantomButton(['all the', 'all the lights'], button_on=16, button_off=12),
    PhantomButton(['downstairs', 'all the downstairs', 'all the lights downstairs'], button_on=1, button_off=1),
    SubScene('entry', ZONES['front door'], 'entry on', 'entry off', dim_scene='entry dim'),
    SubScene('patio', ZONES['backyard'], 'patio', 'path only'),
    SubScene(['patio fireplace', 'backyard fireplace'], ZONES['backyard'], 'fireplace on', 'fireplace off'),
    SubScene(['family room fireplace', 'living room fireplace'], ZONES['family room'], 'fireplace on', 'fireplace off'),
    SubScene('office fireplace', ZONES['office'], 'fireplace on', 'fireplace off'),
    SubScene(['bathroom fan', 'fan'], ZONES['master bathroom'], 'fan on', 'fan off'),
    SubScene(['master fireplace', 'master bedroom fireplace'], ZONES['master bedroom'], 'fireplace on', 'fireplace off')
    ))

VACATION_SCENES = SceneGroup((
    ZONES['powder lights'],
    ZONES['laundry room'],
    ZONES['master bedroom'],
    VIRTUAL_SCENES['entry'],
    VIRTUAL_SCENES['hall'],
    ZONES['exercise room'],
    ZONES['james bedroom'],
    ZONES['master bedroom'],
    ZONES['master bathroom'],
    ZONES['master closet']
    ))

ALEXA_SCENES = SceneGroup()
ALEXA_SCENES.add_scenes(VIRTUAL_SCENES.all_scenes)
ALEXA_SCENES.add_scenes(ZONES.all_scenes)

# There are two unassigned master controls and they give no feedback.  They are the one next to the backyard grafik
# eye and the controller at the landing on the main floor that controls the upstairs (bottom of stairs right)
MASTER_CONTROLS = MasterControlGroup((
    MasterControl('garage', 9, home=1, down=2, all_on=3, vacation=4, leave=5),
    MasterControl('master bedroom', 2, bathroom=1, bathroom_dim=2, pm_snack=3, bedtime=4, master_off=5),
    MasterControl('hall left', 6, main=1, main_dim=2, tv=3, main_all=4, main_off=5),
    MasterControl('hall right', 7, kitchen_nook=1, hall_on=2, hall_entry_off=3, dining=4, entry=5),
    MasterControl('downstairs', 5, stairs=1, rec_room=2, bathroom=3, bedroom=4, all=5),
    MasterControl('bottom of stairs left', 4, main=1, main_dim=2, office=3, entry=4, main_off=5)
))


#
# This method prints the list of scenes that can be controlled by Alexa.
#
def print_automation_parameters():
    print("SHADE_ROOMS")
    for key in SHADES_DICTIONARY.keys():
        print(key)
    print()
    print("LIGHT_SCENES")
    for key in ALEXA_SCENES.keys():
        print(key)
    print()
    print("DIMMABLE_SCENES")
    for key, scene in ALEXA_SCENES.items():
        if scene.supports_dim:
            print(key)
    print()
    print()
    print("PYTHON CODE FOR LAMBAD FUNCTION")
    print("#--------------------------- BEGIN SCENE CODE ---------------------------")
    print()
    print("SHADE_ROOMS = (")
    for key in SHADES_DICTIONARY.keys():
        print('    "{0}",'.format(key))
    print(")")
    print()
    print("LIGHT_SCENES = (")
    for key in ALEXA_SCENES.keys():
        print('    "{0}",'.format(key))
    print(")")
    print()
    print("DIMMABLE_SCENES = (")
    for key, scene in ALEXA_SCENES.items():
        if scene.supports_dim:
            print('    "{0}",'.format(key))
    print(")")
    print()
    print("#---------------------------- END SCENE CODE ----------------------------")
