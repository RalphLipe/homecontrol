from radiora.scene import *
import json


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
# Note that scene names that start with a * are indicate scenes that contain other scenes, but are not themselves
# directly manipulatable.  The only example so far is '*front door' which refers to a Grafik Eye that controls the
# entry and front outdoor lights, but is not something that would be controlled directly.  It is used either by the
# entry scene or the front yard lights scenes.

ZONES = SceneGroup((
    # Main Floor
    GrafikEye(['family room', 'living room'], 13, off=0, on=1, dim=2, fireplace_on=3, fireplace_off=4),
    GrafikEye('office', 15, off=0, on=1, dim=2, fireplace_on=3, fireplace_off=4),
    GrafikEye('kitchen', 10, off=0, on=1, dim=2, cans=3, island=4),
    GrafikEye(['nook', 'breakfast nook'], 11,  off=0, on=1, dim=2, desk=3, table=4),
    GrafikEye('backyard', 12, off=0, on=1, patio=2, fireplace_on=3, path_only=4, fireplace_off=6),
    GrafikEye('*front door', 9, all_off=0, entry_on=1, entry_dim=2, outside_on=3, outside_off=4, entry_off=15),
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
    Dimmer('master toilet', 26),
    Dimmer('master closet', 24, on_setting=70, dim_setting=30),
    Dimmer('packing room', 17),
    Dimmer(['upstairs bathroom', 'nicoles bathroom'], 29),
    Dimmer(['upstairs bedroom', 'nicoles bedroom'], 16),

    # Downstairs
    GrafikEye(['play room', 'pool room', 'rec room'], 14, off=0, on=1, dim=2, cabinets=3, pendants=4),
    Dimmer(['basement cans', 'play room cans', 'pool room cans', 'rec room cans'], 3),
    Dimmer('hall cans', 4),
    Dimmer('hall sconces', 5),
    Dimmer('stair cans', 31),
    Dimmer('stair sconces', 32),
    Dimmer('theater cans', 1),
    Dimmer('theater background', 2),
    Dimmer('exercise room', 18),
    Dimmer(['downstairs bathroom', 'basement bathroom', 'james bathroom'], 23),
    Dimmer(['downstairs bedroom', 'basement bedroom', 'james bedroom'], 19),
    Switch('garage', 22)
    ))

# These scenes need to be declared before VIRTUAL_SCENES because they are used in other composite scenes
_STAIRS_DOWN = CompositeScene('stairs down', (ZONES['hall sconces'], ZONES['stair cans'], ZONES['stair sconces']))
_FRONT_YARD = SubScene(['front yard', 'front outside', 'outside front', 'front'],
                       ZONES['*front door'], 'outside on', 'outside off')
_ENTRY = SubScene('entry', ZONES['*front door'], 'entry on', 'entry off', dim_scene='entry dim')
_MAIN_FLOOR = PhantomButton(['main', 'main floor'], button_on=8, button_off=9, button_dim=14)
_DOWNSTAIRS = PhantomButton(['basement', 'all the basement', 'downstairs', 'all the downstairs',
                             'all the lights downstairs'], button_on=1, button_off=1)
_MASTER_SUITE = CompositeScene(['master suite', 'master'], (ZONES['master bedroom'], ZONES['master bathroom'],
                                                            ZONES['master closet'], ZONES['master toilet']))
_UPSTAIRS = CompositeScene(['all the upstairs', 'all the lights upstairs'], (_MASTER_SUITE, ZONES['stairs up'],
                           ZONES['upstairs bathroom'], ZONES['upstairs bedroom'], ZONES['packing room']))

VIRTUAL_SCENES = SceneGroup((
    _STAIRS_DOWN,
    _FRONT_YARD,
    _ENTRY,
    _MAIN_FLOOR,
    _DOWNSTAIRS,
    _MASTER_SUITE,
    _UPSTAIRS,
    CompositeScene('stairs', (_STAIRS_DOWN, ZONES['stairs up'])),
    CompositeScene(['outside', 'yard', 'outdoor'], (_FRONT_YARD, ZONES['backyard'])),
    CompositeScene(['powder room', 'powder'], (ZONES['powder lights'], ZONES['powder sink'])),
    CompositeScene('kitchen and nook', (ZONES['kitchen'], ZONES['nook'])),
    CompositeScene('theater', (ZONES['theater cans'], ZONES['theater background'])),
    CompositeScene('master bathroom and closet', (ZONES['master bathroom'], ZONES['master toilet'],
                                                  ZONES['master closet'])),
    CompositeScene(['all interior', 'all the interior', 'every interior'], (_UPSTAIRS, _MAIN_FLOOR, _DOWNSTAIRS)),
    PhantomButton('hall', button_on=4, button_off=5),
    PhantomButton(['all the', 'all the lights'], button_on=16, button_off=12),
    SubScene('patio', ZONES['backyard'], 'patio', 'path only'),
    SubScene(['patio fireplace', 'backyard fireplace'], ZONES['backyard'], 'fireplace on', 'fireplace off'),
    SubScene(['family room fireplace', 'living room fireplace'], ZONES['family room'], 'fireplace on', 'fireplace off'),
    SubScene('office fireplace', ZONES['office'], 'fireplace on', 'fireplace off'),
    SubScene(['bathroom fan', 'fan'], ZONES['master bathroom'], 'fan on', 'fan off'),
    SubScene(['master fireplace', 'master bedroom fireplace'],
             ZONES['master bedroom'], 'fireplace on', 'fireplace off'),
    UseScene('watch tv',
             dim=[ZONES['kitchen'], ZONES['family room'], ZONES['end of hall']],
             off=[_ENTRY, ZONES['dining']]),
    UseScene(['watch movie', 'watch a movie'], dim=[ZONES['theater background']], off=[ZONES['theater cans']]),
    UseScene('bedtime',
             off=[_MAIN_FLOOR, _DOWNSTAIRS, ZONES['stairs up'], ZONES['packing room'], ZONES['upstairs bedroom']])
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

ALL_SCENES = SceneGroup()
ALL_SCENES.add_scenes(ZONES.all_scenes)
ALL_SCENES.add_scenes(VIRTUAL_SCENES.all_scenes)


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
    for key in ALL_SCENES.keys():
        if key[0] != '*':   # All scenes that start with a * should not be used for voice UI
            print(key)
    print()
    print("DIMMABLE_SCENES")
    for key, scene in ALL_SCENES.items():
        if scene.supports_dim:
            print(key)
    print()
    print()
    print("PYTHON CODE FOR LAMBDA FUNCTION")
    print("#--------------------------- BEGIN SCENE CODE ---------------------------")
    print()
    print("SHADE_ROOMS = (")
    for key in SHADES_DICTIONARY.keys():
        print('    "{0}",'.format(key))
    print(")")
    print()
    print("LIGHT_SCENES = (")
    for key in ALL_SCENES.keys():
        if key[0] != '*':   # All scenes that start with a * should not be used for voice UI
            print('    "{0}",'.format(key))
    print(")")
    print()
    print("DIMMABLE_SCENES = (")
    for key, scene in ALL_SCENES.items():
        if scene.supports_dim:
            print('    "{0}",'.format(key))
    print(")")
    print()
    print("#---------------------------- END SCENE CODE ----------------------------")


def save_scenes(file):
    with open(file, 'w') as scenes_file:
        json.dump(ALL_SCENES.to_list(), scenes_file, indent=4)


def save_shades(file):
    with open(file, 'w') as shades_file:
        json.dump(list(SHADES_DICTIONARY.keys()), shades_file, indent=4)
