#!/usr/bin/env python3

"""
Image sources (see also info message):
    http://forums.eagle.ru/showthread.php?t=102016

Other's efforts:
    https://github.com/subn3t/warthog
    ... at http://subn3t.com/warthog/  -- doesn't do all the keys!
"""

# =============================================================================
# Imports
# =============================================================================

import argparse
import json
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
from xml.etree import ElementTree

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)  # install with "pip3 install pillow" but import as PIL

# =============================================================================
# Defaults
# =============================================================================

DEFAULT_JOYSTICK_TEMPLATE = "templates/TEMPLATE_tmw_joystick.png"
DEFAULT_THROTTLE_TEMPLATE = "templates/TEMPLATE_tmw_throttle.png"
DEFAULT_JOYSTICK_OUTPUT = "output/output_joystick.png"
DEFAULT_THROTTLE_OUTPUT = "output/output_throttle.png"
DEFAULT_COMPOSITE_OUTPUT = "output/output_composite.png"

DEFAULT_TRUETYPE_FILE = "Arial_Bold.ttf"
DEFAULT_RGB_ANALOGUE = "255,0,255"
DEFAULT_RGB_MOMENTARY = "255,0,0"
DEFAULT_RGB_STICKY = "0,0,255"

DEFAULT_ED_STICK = "ThrustMasterWarthogJoystick"
DEFAULT_ED_THROTTLE = "ThrustMasterWarthogThrottle"
DEFAULT_ED_MFG_CROSSWIND_NAME = "16D00A38"  # always this value or not?

# =============================================================================
# Other constants
# =============================================================================

J_WIDTH = 190
J_HEIGHT = 50
T_WIDTH = 155
T_HEIGHT = 35
T_IDLE_WIDTH = 114
T_IDLE_HEIGHT = 22
T_THUMBHAT_WIDTH = 125
T_THUMBHAT_HEIGHT = 29
T_OTHERTHUMB_WIDTH = 140
T_OTHERTHUMB_HEIGHT = 29

TMW_STICK_NAME = "thrustmaster_warthog_joystick"
TMW_THROTTLE_NAME = "thrustmaster_warthog_throttle"
MFG_CROSSWIND_NAME = "mfg_crosswind_pedals"

RECT_OUTLINE = (0, 0, 0)
RECT_FILL = (240, 240, 240)

ANALOGUE = '~'
MOMENTARY = '.'
STICKY = '+'

# =============================================================================
# Devices, with mappings to picture coordinates, Elite Dangerous names, etc.
# =============================================================================

TMW_STICK_MAP = {
    # Dictionary attributes:
    #   l, t = left, top edge of text box
    #   w, h = width, height of text box
    #   ed = Elite Dangerous key name
    #   type = '~' analogue, '.' momentary switch, '+' sticky switch

    # overall image size is 1625 x 2201

    'Stick_Forward': dict(
        l=213, t=1386, w=J_WIDTH, h=J_HEIGHT, ed='Joy_YAxis', type=ANALOGUE),
    'Stick_Backward': dict(
        l=189, t=1710, w=J_WIDTH, h=J_HEIGHT, ed='Joy_YAxis', type=ANALOGUE),
    'Stick_Left': dict(
        l=39, t=1592, w=J_WIDTH, h=J_HEIGHT, ed='Joy_XAxis', type=ANALOGUE),
    'Stick_Right': dict(
        l=377, t=1608, w=J_WIDTH, h=J_HEIGHT, ed='Joy_XAxis', type=ANALOGUE),

    'TrimHat_Up': dict(
        l=1151, t=107, w=J_WIDTH, h=J_HEIGHT, ed='Joy_POV1Up', type=MOMENTARY),
    'TrimHat_Left': dict(
        l=909, t=254, w=J_WIDTH, h=J_HEIGHT, ed='Joy_POV1Left',
        type=MOMENTARY),
    'TrimHat_Right': dict(
        l=1380, t=254, w=J_WIDTH, h=J_HEIGHT, ed='Joy_POV1Right',
        type=MOMENTARY),
    'TrimHat_Down': dict(
        l=1151, t=399, w=J_WIDTH, h=J_HEIGHT, ed='Joy_POV1Down',
        type=MOMENTARY),

    # Not sure these are actually valid
    'TrimHat_UpLeft': dict(l=942, t=170, w=J_WIDTH, h=J_HEIGHT),
    'TrimHat_UpRight': dict(l=1355, t=170, w=J_WIDTH, h=J_HEIGHT),
    'TrimHat_DownLeft': dict(l=942, t=329, w=J_WIDTH, h=J_HEIGHT),
    'TrimHat_DownRight': dict(l=1355, t=329, w=J_WIDTH, h=J_HEIGHT),

    'S1_Trigger_FirstStage': dict(
        l=726, t=1739, w=J_WIDTH, h=J_HEIGHT, ed='Joy_1', type=MOMENTARY),
    'S2_WeaponsRelease': dict(
        l=275, t=339, w=J_WIDTH, h=J_HEIGHT, ed='Joy_2', type=MOMENTARY),
    'S3_NSB': dict(  # nosewheel steering button
        l=1346, t=1866, w=J_WIDTH, h=J_HEIGHT, ed='Joy_3', type=MOMENTARY),

    'S4_PinkieLever': dict(
        l=1308, t=1983, w=J_WIDTH, h=J_HEIGHT, ed='Joy_4', type=MOMENTARY),
    'S5_MMC': dict(  # master mode control
        l=1224, t=560, w=J_WIDTH, h=J_HEIGHT, ed='Joy_5', type=MOMENTARY),
    'S6_Trigger_SecondStage': dict(
        l=774, t=1871, w=J_WIDTH, h=J_HEIGHT, ed='Joy_6', type=MOMENTARY),
    # Target management switch
    'S7_TMS_Up': dict(
        l=242, t=501, w=J_WIDTH, h=J_HEIGHT, ed='Joy_7', type=MOMENTARY),
    'S8_TMS_Right': dict(
        l=419, t=603, w=J_WIDTH, h=J_HEIGHT, ed='Joy_8', type=MOMENTARY),
    'S9_TMS_Down': dict(
        l=242, t=708, w=J_WIDTH, h=J_HEIGHT, ed='Joy_9', type=MOMENTARY),
    'S10_TMS_Left': dict(
        l=62, t=603, w=J_WIDTH, h=J_HEIGHT, ed='Joy_10', type=MOMENTARY),
    # Data management switch
    'S11_DMS_Up': dict(
        l=1187, t=729, w=J_WIDTH, h=J_HEIGHT, ed='Joy_11', type=MOMENTARY),
    'S12_DMS_Right': dict(
        l=1365, t=833, w=J_WIDTH, h=J_HEIGHT, ed='Joy_12', type=MOMENTARY),
    'S13_DMS_Down': dict(
        l=1187, t=938, w=J_WIDTH, h=J_HEIGHT, ed='Joy_13', type=MOMENTARY),
    'S14_DMS_Left': dict(
        l=1007, t=833, w=J_WIDTH, h=J_HEIGHT, ed='Joy_14', type=MOMENTARY),
    # Countermeasures management switch
    'S15_CMS_Forward': dict(
        l=246, t=1044, w=J_WIDTH, h=J_HEIGHT, ed='Joy_15', type=MOMENTARY),
    'S16_CMS_Right': dict(
        l=426, t=1148, w=J_WIDTH, h=J_HEIGHT, ed='Joy_16', type=MOMENTARY),
    'S17_CMS_Backward': dict(
        l=84, t=1256, w=J_WIDTH, h=J_HEIGHT, ed='Joy_17', type=MOMENTARY),
    'S18_CMS_Left': dict(
        l=65, t=1148, w=J_WIDTH, h=J_HEIGHT, ed='Joy_18', type=MOMENTARY),
    'S19_CMS_Press': dict(
        l=327, t=1263, w=J_WIDTH, h=J_HEIGHT, ed='Joy_19', type=MOMENTARY),
}
MFG_CROSSWIND_MAP = {
    # These are specials from the MFG Crosswind:
    'Rudder': dict(
        l=325, t=1850, w=J_WIDTH, h=J_HEIGHT, hjust=0,
        ed='Joy_RZAxis', type=ANALOGUE),
    'LeftFootbrake': dict(
        l=325, t=1925, w=J_WIDTH, h=J_HEIGHT, hjust=0,
        ed='Joy_XAxis', type=ANALOGUE),
    'RightFootbrake': dict(
        l=325, t=2000, w=J_WIDTH, h=J_HEIGHT, hjust=0,
        ed='Joy_YAxis', type=ANALOGUE),
}
CROSSWIND_EXTRA_LABELS = [
    dict(text='Pedals: Rudder',
         x=300, y=1850 + J_HEIGHT/2, fontsize=20, rgb=(0, 0, 0),
         hjust=1, vjust=0.5),
    dict(text='Pedals: Left footbrake',
         x=300, y=1925 + J_HEIGHT/2, fontsize=20, rgb=(0, 0, 0),
         hjust=1, vjust=0.5),
    dict(text='Pedals: Right footbrake',
         x=300, y=2000 + J_HEIGHT/2, fontsize=20, rgb=(0, 0, 0),
         hjust=1, vjust=0.5),
]
TMW_THROTTLE_MAP = {
    # overall image size is 1625 x 2201

    'LeftThrottle': dict(
        l=1131, t=2130, w=T_WIDTH, h=T_HEIGHT, ed='Joy_RZAxis', type=ANALOGUE),
    'RightThrottle': dict(
        l=593, t=2130, w=T_WIDTH, h=T_HEIGHT, ed='Joy_ZAxis', type=ANALOGUE),

    'CoolieSwitchUp': dict(
        l=553, t=1318, w=T_WIDTH, h=T_HEIGHT, ed='Joy_POV1Up', type=MOMENTARY),
    'CoolieSwitchDown': dict(
        l=553, t=1539, w=T_WIDTH, h=T_HEIGHT, ed='Joy_POV1Down',
        type=MOMENTARY),
    'CoolieSwitchLeft': dict(
        l=730, t=1429, w=T_WIDTH, h=T_HEIGHT, ed='Joy_POV1Left',
        type=MOMENTARY),
    'CoolieSwitchRight': dict(
        l=379, t=1429, w=T_WIDTH, h=T_HEIGHT, ed='Joy_POV1Right',
        type=MOMENTARY),

    'CoolieSwitchUpLeft': dict(l=713, t=1371, w=T_WIDTH, h=T_HEIGHT),
    'CoolieSwitchUpRight': dict(l=400, t=1371, w=T_WIDTH, h=T_HEIGHT),
    'CoolieSwitchDownLeft': dict(l=713, t=1486, w=T_WIDTH, h=T_HEIGHT),
    'CoolieSwitchDownRight': dict(l=400, t=1486, w=T_WIDTH, h=T_HEIGHT),

    'ThrottleFrictionControl': dict(
        l=1361, t=697, w=T_WIDTH, h=T_HEIGHT, ed='Joy_UAxis', type=ANALOGUE),

    'SlewControl_LeftRight': dict(
        l=1156, t=1444, w=T_WIDTH, h=T_HEIGHT, ed='Joy_XAxis', type=ANALOGUE),
    'SlewControl_UpDown': dict(
        l=1056, t=1348, w=T_WIDTH, h=T_HEIGHT, ed='Joy_YAxis', type=ANALOGUE),

    'S1_SlewControl_Press': dict(
        l=957, t=1571, w=T_WIDTH, h=T_HEIGHT, ed='Joy_1', type=MOMENTARY),
    'S2_ThumbHat_Press': dict(
        l=285, t=1707, w=T_THUMBHAT_WIDTH, h=T_THUMBHAT_HEIGHT, ed='Joy_2',
        type=MOMENTARY),
    'S3_ThumbHat_Up': dict(
        l=233, t=1567, w=T_THUMBHAT_WIDTH, h=T_THUMBHAT_HEIGHT, ed='Joy_3',
        type=MOMENTARY),
    'S4_ThumbHat_Forward': dict(
        l=346, t=1633, w=T_THUMBHAT_WIDTH, h=T_THUMBHAT_HEIGHT, ed='Joy_4',
        type=MOMENTARY),
    'S5_ThumbHat_Down': dict(
        l=129, t=1701, w=T_THUMBHAT_WIDTH, h=T_THUMBHAT_HEIGHT, ed='Joy_5',
        type=MOMENTARY),
    'S6_ThumbHat_Backward': dict(
        l=117, t=1633, w=T_THUMBHAT_WIDTH, h=T_THUMBHAT_HEIGHT, ed='Joy_6',
        type=MOMENTARY),
    'S7_Speedbrake_Forward': dict(
        l=230, t=1758, w=T_OTHERTHUMB_WIDTH, h=T_OTHERTHUMB_HEIGHT,
        ed='Joy_7', type=STICKY),
    'S8_Speedbrake_Backward': dict(
        l=230, t=1804, w=T_OTHERTHUMB_WIDTH, h=T_OTHERTHUMB_HEIGHT,
        ed='Joy_8', type=MOMENTARY),
    'S9_BoatSwitch_Forward': dict(
        l=230, t=1857, w=T_OTHERTHUMB_WIDTH, h=T_OTHERTHUMB_HEIGHT,
        ed='Joy_9', type=STICKY),
    'S10_BoatSwitch_Backward': dict(
        l=230, t=1903, w=T_OTHERTHUMB_WIDTH, h=T_OTHERTHUMB_HEIGHT,
        ed='Joy_10', type=STICKY),
    'S11_ChinaHat_Forward': dict(
        l=230, t=1957, w=T_OTHERTHUMB_WIDTH, h=T_OTHERTHUMB_HEIGHT,
        ed='Joy_11', type=MOMENTARY),
    'S12_ChinaHat_Backward': dict(
        l=230, t=2003, w=T_OTHERTHUMB_WIDTH, h=T_OTHERTHUMB_HEIGHT,
        ed='Joy_12', type=MOMENTARY),
    'S13_PinkieSwitch_Forward': dict(
        l=1396, t=1901, w=T_WIDTH, h=T_HEIGHT, ed='Joy_13', type=STICKY),
    'S14_PinkieSwitch_Backward': dict(
        l=1396, t=1963, w=T_WIDTH, h=T_HEIGHT, ed='Joy_14', type=STICKY),
    'S15_LeftThrottleButton': dict(
        l=1352, t=1526, w=T_WIDTH, h=T_HEIGHT, ed='Joy_15', type=MOMENTARY),
    'S16_LeftEngineFuelFlow': dict(
        l=653, t=70, w=T_WIDTH, h=T_HEIGHT, ed='Joy_16', type=STICKY),
    'S17_RightEngineFuelFlow': dict(
        l=879, t=70, w=T_WIDTH, h=T_HEIGHT, ed='Joy_17', type=STICKY),
    'S18_LeftEngineOperateDown': dict(
        l=1341, t=412, w=T_WIDTH, h=T_HEIGHT, ed='Joy_18', type=STICKY),
    'S19_RightEngineOperateDown': dict(
        l=1341, t=529, w=T_WIDTH, h=T_HEIGHT, ed='Joy_19', type=STICKY),
    'S20_APUStart': dict(  # APU = auxiliary power unit
        l=1237, t=593, w=T_WIDTH, h=T_HEIGHT, ed='Joy_20', type=STICKY),
    'S21_LandingGearWarningSilence': dict(
        l=1333, t=792, w=T_WIDTH, h=T_HEIGHT, ed='Joy_21', type=MOMENTARY),
    'S22_FlapsUp': dict(
        l=209, t=741, w=T_WIDTH, h=T_HEIGHT, ed='Joy_22', type=STICKY),
    'S23_FlapsDown': dict(
        l=209, t=795, w=T_WIDTH, h=T_HEIGHT, ed='Joy_23', type=STICKY),
    'S24_EAC': dict(  # Enhanced Attitude Control
        l=175, t=1043, w=T_WIDTH, h=T_HEIGHT, ed='Joy_24', type=STICKY),
    'S25_RadarAltimeter': dict(
        l=349, t=1234, w=T_WIDTH, h=T_HEIGHT, ed='Joy_25', type=STICKY),
    'S26_AutopilotEngageDisengage': dict(
        l=1038, t=1234, w=T_WIDTH, h=T_HEIGHT, ed='Joy_26', type=MOMENTARY),
    'S27_AutopilotMode_Up': dict(
        l=1359, t=989, w=T_WIDTH, h=T_HEIGHT, ed='Joy_27', type=STICKY),
    'S28_AutopilotMode_Down': dict(
        l=1359, t=1043, w=T_WIDTH, h=T_HEIGHT, ed='Joy_28', type=STICKY),
    'S29_RightEngineIdle': dict(
        l=569, t=713, w=T_IDLE_WIDTH, h=T_IDLE_HEIGHT, ed='Joy_29',
        type=STICKY),
    'S30_LeftEngineIdle': dict(
        l=787, t=713, w=T_IDLE_WIDTH, h=T_IDLE_HEIGHT, ed='Joy_30',
        type=STICKY),
    'S31_LeftEngineOperateUp': dict(
        l=1341, t=354, w=T_WIDTH, h=T_HEIGHT, ed='Joy_31', type=MOMENTARY),
    'S32_RightEngineOperateUp': dict(
        l=1341, t=471, w=T_WIDTH, h=T_HEIGHT, ed='Joy_32', type=MOMENTARY),
}

# =============================================================================
# Map E:D labels to human
# =============================================================================

ED_LABEL_MAP = {
    'AheadThrust_Landing': 'Ldg/Thrust fwd/back',
    'AheadThrust': 'Thrust fwd/back',
    'BackwardKey': 'Backward',
    'BackwardThrustButton_Landing': 'Ldg/Thrust back',
    'BackwardThrustButton': 'Thrust back',
    'CamPitchAxis': 'Cam. pitch',
    'CamPitchDown': 'Cam. pitch down',
    'CamPitchUp': 'Cam. pitch up',
    'CamTranslateBackward': 'Cam. backward',
    'CamTranslateDown': 'Cam. xlate down',
    'CamTranslateForward': 'Cam. forward',
    'CamTranslateLeft': 'Cam. xlate L',
    'CamTranslateRight': 'Cam. xlate R',
    'CamTranslateUp': 'Cam. xlate up',
    'CamTranslateXAxis': 'Cam. xlate L/R',
    'CamTranslateYAxis': 'Cam. xlate fwd/back',  # *** check
    'CamTranslateZAxis': 'Cam. xlate up/down',
    'CamTranslateZHold': 'Cam. xlate Z hold',
    'CamYawAxis': 'Cam. yaw',
    'CamYawLeft': 'Cam. yaw L',
    'CamYawRight': 'Cam. yaw R',
    'CamZoomAxis': 'Cam. zoom',
    'CamZoomIn': 'Cam. zoom in',
    'CamZoomOut': 'Cam. zoom out',
    'CycleFireGroupNext': 'Next firegroup',
    'CycleFireGroupPrevious': 'Prev. firegroup',
    'CycleNextHostileTarget': 'Next hostile target',
    'CycleNextPanel': 'UI next panel',
    'CycleNextSubsystem': 'Next target subsyst.',
    'CycleNextTarget': 'Next target',
    'CyclePreviousHostileTarget': 'Prev. hostile target',
    'CyclePreviousPanel': 'UI prev. panel',
    'CyclePreviousSubsystem': 'Prev. target subsyst.',
    'CyclePreviousTarget': 'Prev. target',
    'DeployHardpointToggle': 'Hardpoints ±',
    'DeployHeatSink': 'Heatsink',
    'DisableRotationCorrectToggle': 'Rotat. correction',
    'DownThrustButton_Landing': 'Ldg/Thrust down',
    'DownThrustButton': 'Thrust down',
    'EjectAllCargo': 'Eject cargo',
    'FireChaffLauncher': 'Chaff',
    'FocusCommsPanel': 'UI COMMS panel',
    'FocusLeftPanel': 'UI LEFT panel',
    'FocusRadarPanel': 'UI RADAR panel',
    'FocusRightPanel': 'UI RIGHT panel',
    'ForwardKey': 'Forward',
    'ForwardThrustButton_Landing': 'Ldg/Thrust fwd',
    'GalaxyMapOpen': 'Galaxy map',
    'HeadLookPitchAxisRaw': 'Headlook up/down',
    'HeadLookPitchDown': 'Headlook down',
    'HeadLookPitchUp': 'Headlook up',
    'HeadLookReset': 'Reset headlook',
    'HeadLookToggle': 'Headlook ±',
    'HeadLookYawAxis': 'Headlook L/R',
    'HeadLookYawLeft': 'Headlook L',
    'HeadLookYawRight': 'Headlook R',
    'HMDReset': 'Reset VR orientation',  # *** I think
    'HyperSuperCombination': 'Frame Shift Drive ±',
    'IncreaseEnginesPower': 'Pwr→ENGINES',
    'IncreaseSystemsPower': 'Pwr→SYSTEMS',
    'IncreaseWeaponsPower': 'Pwr→WEAPONS',
    'LandingGearToggle': 'Landing gear ±',
    'LateralThrustAlternate': 'Lateral thrust (ALT)',
    'LateralThrust_Landing': 'Ldg/Lateral thrust',
    'LateralThrustRaw': 'Lateral thrust',
    'LeftThrustButton_Landing': 'Ldg/Thrust L',
    'LeftThrustButton': 'Thrust L',
    'MicrophoneMute': 'Mic. mute',
    'OrbitLinesToggle': 'Orbit lines ±',
    'PhotoCameraToggle': 'Camera view ±',
    'PitchAxisAlternate': 'Pitch (ALT)',
    'PitchAxis_Landing': 'Ldg/Pitch',
    'PitchAxisRaw': 'Pitch',
    'PitchDownButton_Landing': 'Ldg/Pitch down',
    'PitchDownButton': 'Pitch down',
    'PitchUpButton_Landing': 'Ldg/Pitch up',
    'PitchUpButton': 'Pitch up',
    'PrimaryFire': 'Fire 1',
    'QuickCommsPanel': 'Quick comms',
    'RadarDecreaseRange': 'Radar +',
    'RadarIncreaseRange': 'Radar -',
    'RadarRangeAxis': 'Radar range',
    'ResetPowerDistribution': 'Balance pwr distrib.',
    'RightThrustButton_Landing': 'Ldg/Thrust R',
    'RightThrustButton': 'Thrust R',
    'RollAxisAlternate': 'Roll (ALT)',
    'RollAxis_Landing': 'Ldg/Roll',
    'RollAxisRaw': 'Roll',
    'RollLeftButton_Landing': 'Ldg/Roll L',
    'RollLeftButton': 'Roll L',
    'RollRightButton_Landing': 'Ldg/Roll R',
    'RollRightButton': 'Roll R',
    'SecondaryFire': 'Fire 2',
    'SelectHighestThreat': 'Highest threat',
    'SelectTargetsTarget': "Target's target",
    'SelectTarget': 'Target ahead',
    'SetSpeed100': 'Speed 100%',
    'SetSpeed25': 'Speed 25%',
    'SetSpeed25': 'Speed 25%',
    'SetSpeed50': 'Speed 50%',
    'SetSpeed75': 'Speed 75%',
    'SetSpeedMinus100': 'Speed –100%',
    'SetSpeedMinus25': 'Speed –25%',
    'SetSpeedMinus50': 'Speed –50%',
    'SetSpeedMinus75': 'Speed –75%',
    'SetSpeedZero': 'Speed 0%',
    'ShipSpotLightToggle': 'Lights ±',
    'ShowPGScoreSummaryInput': 'ShowPGScoreSummaryInput',  # *** ??
    'SystemMapOpen': 'System map',
    'TargetNextRouteSystem': 'Next system in route',
    'TargetWingman0': 'Wingman 1',
    'TargetWingman1': 'Wingman 2',
    'TargetWingman2': 'Wingman 3',
    'ThrottleAxis': 'Throttle',
    'ToggleButtonUpInput': 'Silent running',
    'ToggleCargoScoop': 'Cargo scoop',
    'ToggleFlightAssist': 'Flight Assist',
    'ToggleReverseThrottleInput': 'Reverse throttle',
    'UI_Back': 'UI back',
    'UI_Down': 'UI down',
    'UIFocus': 'UI focus',
    'UI_Left': 'UI left',
    'UI_Right': 'UI right',
    'UI_Select': 'UI select',
    'UI_Up': 'UI up',
    'UpThrustButton_Landing': 'Ldg/Thrust up',
    'UpThrustButton': 'Thrust up',
    'UseAlternateFlightValuesToggle': 'Toggle ALT flight controls',
    'UseBoostJuice': 'Engine boost',
    'UseShieldCell': 'Shield cell',
    'VerticalThrustAlternate': 'Vertical thrust (ALT)',
    'VerticalThrust_Landing': 'Ldg/Vertical thrust',
    'VerticalThrustRaw': 'Vertical thrust',
    'WingNavLock': 'Wingman nav lock',
    'YawAxisRaw': 'Yaw',
    'YawLeftButton_Landing': 'Ldg/Yaw L',
    'YawLeftButton': 'Yaw L',
    'YawRightButton_Landing': 'Ldg/Yaw R',
    'YawRightButton': 'Yaw R',

    # Those for E:D Horizons surface buggy, below, are guesswork.
    # SRV = surface reconnaissance vehicle
    'AutoBreakBuggyButton': 'SRV Handbrake',  # unsure
    'BuggyPitchAxis': 'SRV Pitch',
    'BuggyPrimaryFireButton': 'SRV Fire 1',
    'BuggyRollAxisRaw': 'SRV Roll',
    'BuggySecondaryFireButton': 'SRV Fire 2',
    'BuggyToggleReverseThrottleInput': 'SRV Reverse throttle',
    'BuggyTurretPitchDownButton': 'SRV Turret down',
    'BuggyTurretPitchUpButton': 'SRV Turret up',
    'BuggyTurretYawLeftButton': 'SRV Turret L',
    'BuggyTurretYawRightButton': 'SRV Turret R',
    'DriveSpeedAxis': 'SRV Speed',
    'HeadlightsBuggyButton': 'SRV Headlights ±',
    'SelectTarget_Buggy': 'SRV Target ahead',
    'SteeringAxis': 'SRV Steering',
    'ToggleBuggyTurretButton': 'SRV Toggle turret',
    'ToggleDriveAssist': 'SRV Drive Assist',
    'VerticalThrustersButton': 'SRV Vertical Thrusters',
}
ED_HORIZONS = [  # Labels to ignore for now
    # Probably from E:D Horizons:
    'AutoBreakBuggyButton',
    'BuggyPitchAxis',
    'BuggyPrimaryFireButton',
    'BuggyRollAxisRaw',
    'BuggySecondaryFireButton',
    'BuggyToggleReverseThrottleInput',
    'BuggyTurretPitchDownButton',
    'BuggyTurretPitchUpButton',
    'BuggyTurretYawLeftButton',
    'BuggyTurretYawRightButton',
    'DriveSpeedAxis',
    'HeadlightsBuggyButton',
    'SelectTarget_Buggy',
    'SteeringAxis',
    'ToggleBuggyTurretButton',
    'ToggleDriveAssist',
    # Unsure:
    'VerticalThrustersButton',
]


# =============================================================================
# Helper functions: language
# =============================================================================

def merge_dicts(*args):
    """Creates a new dictionary that merges those passed as arguments."""
    if not args:
        return {}
    d = args[0].copy()
    for extra in args[1:]:
        d.update(extra)
    return d


def rgb_tuple_from_csv(text):
    """Returns a three-valued tuple, each in the range 0-255, from comma-
    separated text."""
    values = text.split(",")
    if len(values) != 3:
        raise ValueError("Not a tuple of length 3")
    values = [int(v) for v in values]
    for v in values:
        if not (0 <= v <= 255):
            raise ValueError("Value not in range 0-255")
    return tuple(values)


# =============================================================================
# Helper functions: pillow
# =============================================================================

def get_text_width_height(font, text):
    """Return a more accurate (width, height) for a PIL font object than its
    getsize() method."""
    if "\n" in text:
        fragments = text.split("\n")
        sizes = []
        for f in fragments:
            sizes.append(font.getsize(f))
        textwidth = max([x[0] for x in sizes])
        textheight = sum([x[1] for x in sizes])
    else:
        textwidth, textheight = font.getsize(text)
    return (textwidth, textheight)


def composite_side_by_side(joinedfilename, filenames):
    """Composite two or more images side-by-side."""
    logger.info("Compositing {} -> {}".format(filenames, joinedfilename))
    images = [Image.open(f) for f in filenames]
    width = sum(i.size[0] for i in images)
    height = max(i.size[1] for i in images)
    logger.debug("width={}, height={}".format(width, height))
    joined = Image.new('RGB', (width, height))
    x = 0
    for i in images:
        logger.debug("pasting at x={}".format(x))
        joined.paste(i, (x, 0))
        x += i.size[0]
    joined.save(joinedfilename)


def justify_to_point(point, itemsize, just=0):
    """
    just:
        0 = left/top
        0.5 = centre
        1 = right/bottom
    returns: starting coordinate (top or left)
    Note:
        x axis is left-to-right (and justification 0-1 is left-to-right)
        y axis is top-to-bottom (and justification 0-1 is top-to-bottom)
        ... so we can treat them equivalently.
    """
    return point - itemsize * just


def justify_to_box(boxstart, boxsize, itemsize, just=0):
    """
    Justifies, similarly, but within a box.
    """
    return boxstart + (boxsize - itemsize) * just


def add_label(img, text, x, y, ttf, fontsize, rgb,
              hjust=0, vjust=0):
    """Adds a label to an image."""
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(ttf, fontsize)
    except:
        logger.error("Failed to load font!")
        raise
    w, h = get_text_width_height(font, text)
    x = justify_to_point(x, w, hjust)
    y = justify_to_point(y, h, vjust)
    draw.text((x, y), text, rgb, font=font)


def add_boxed_text(img, text, boxcoords, ttf, rgb,
                   showrect=False, hjust=0.5, vjust=0.5):
    """Adds text to an image, within a notional rectangle."""
    logger.debug("add_boxed_text: text={}, boxcoords={}".format(
        repr(text), repr(boxcoords)))
    draw = ImageDraw.Draw(img)
    boxleft, boxtop, boxwidth, boxheight = boxcoords
    BASE_FONTSIZE = 16
    try:
        font = ImageFont.truetype(ttf, BASE_FONTSIZE)
    except:
        logger.error("Failed to load font!")
        raise
    basetextwidth, basetextheight = get_text_width_height(font, text)
    if basetextwidth/boxwidth > basetextheight/boxheight:
        # Text is wider (as a proportion of the box) than tall.
        fontsize = int(BASE_FONTSIZE * boxwidth/basetextwidth)
    else:
        # Text is taller (as a proportion of the box) than wide.
        fontsize = int(BASE_FONTSIZE * boxheight/basetextheight)
    font = ImageFont.truetype(ttf, fontsize)
    textwidth, textheight = get_text_width_height(font, text)
    logger.debug("Final fontsize {} (text width {}, text height {})".format(
        fontsize, textwidth, textheight))
    if showrect:
        draw.rectangle(
            [(boxleft, boxtop), (boxleft + boxwidth, boxtop + boxheight)],
            outline=RECT_OUTLINE,
            fill=RECT_FILL
        )
    x = justify_to_box(boxleft, boxwidth, textwidth, hjust)
    y = justify_to_box(boxtop, boxheight, textheight, vjust)
    draw.text((x, y), text, rgb, font=font)


# =============================================================================
# Core processing functions
# =============================================================================

def get_mapping(cmdargs):
    if cmdargs.format == 'json':
        logger.info("Using JSON input file {}".format(cmdargs.input))
        json_data = open(cmdargs.input).read()
        return json.loads(json_data)
    elif cmdargs.format == 'demo':
        logger.info("Using demo mapping")
        return {
            TMW_STICK_NAME: dict([(k, [k]) for k in TMW_STICK_MAP.keys()]),
            TMW_THROTTLE_NAME: dict([(k, [k])
                                     for k in TMW_THROTTLE_MAP.keys()]),
            MFG_CROSSWIND_NAME: dict([(k, [k])
                                      for k in MFG_CROSSWIND_MAP.keys()]),
        }
    elif cmdargs.format == 'ed':
        logger.info("Using Elite Dangerous binding file {}".format(
            cmdargs.input))
        masterdict = {
            TMW_STICK_NAME: {},
            TMW_THROTTLE_NAME: {},
            MFG_CROSSWIND_NAME: {},
        }
        tree = ElementTree.parse(cmdargs.input)
        root = tree.getroot()
        # Nodes look like this:
        #   <FUNCTIONNAME>
        #       <Primary Device="DEVICENAME" Key="KEYNAME" />
        #       <Secondary Device="DEVICENAME" Key="KEYNAME" />
        #   </FUNCTIONNAME>
        #   <FUNCTIONNAME>
        #       <Binding Device="DEVICENAME" Key="KEYNAME" />
        #   </FUNCTIONNAME>
        # Find all nodes that have a child named "Primary"
        # Some have 'Buggy' in them... presumably relate to a rover buggy
        # on planetary surfaces, rather than duff keys!
        nodes = root.findall("./*")
        logger.debug("XML nodes: {}".format(nodes))
        for node in nodes:
            for childbit in ['Primary', 'Secondary', 'Binding']:
                child = node.find("./" + childbit)
                if child is not None and (cmdargs.ed_horizons
                                          or node.tag not in ED_HORIZONS):
                    process_ed_xml_node(node.tag, child, masterdict, cmdargs)
        return masterdict
    else:
        assert False, "Bad input format: {}".format(cmdargs.format)


def process_ed_xml_node(parenttag, node, masterdict, cmdargs):
    device = node.attrib['Device']
    key = node.attrib['Key']
    logger.debug("Processing node: {}, device={}, key={}".format(
        parenttag, device, key))
    if device == cmdargs.ed_tmw_stick:
        refmap = TMW_STICK_MAP
        refdict = masterdict[TMW_STICK_NAME]
    elif device == cmdargs.ed_tmw_throttle:
        refmap = TMW_THROTTLE_MAP
        refdict = masterdict[TMW_THROTTLE_NAME]
    elif device == cmdargs.ed_mfg_crosswind:
        refmap = MFG_CROSSWIND_MAP
        refdict = masterdict[MFG_CROSSWIND_NAME]
    else:
        return
    for ourkey, ourdict in refmap.items():
        if ourdict.get('ed') == key:
            logger.debug("Found: ourkey={}".format(ourkey))
            if ourkey not in refdict:
                refdict[ourkey] = []
            nicelabel = ED_LABEL_MAP.get(parenttag, parenttag)
            refdict[ourkey].append(nicelabel)


def make_picture(descmap, placemap, template, outfile, cmdargs,
                 extralabels=None):
    """
    descmap: dict mapping keyname -> description
    placemap: dict mapping keyname -> dict(l=left, r=right, t=top, b=bottom)
    template: template file
    outfile: output file
    """
    extralabels = extralabels or []
    logger.info("Opening template: {}".format(template))
    img = Image.open(template)
    logger.debug("Image size: {}".format(img.size))
    logger.debug("descmap: {}".format(descmap))
    for key, desclist in descmap.items():
        if key in placemap:
            info = placemap[key]
            boxleft = info['l']
            boxtop = info['t']
            boxwidth = info['w']
            boxheight = info['h']
            type = info.get('type')
            if type == ANALOGUE:
                rgb = cmdargs.rgbanalogue
            elif type == STICKY:
                rgb = cmdargs.rgbsticky
            else:
                rgb = cmdargs.rgbmomentary
            boxcoords = (boxleft, boxtop, boxwidth, boxheight)
            desc = "\n".join(desclist)
            add_boxed_text(img, desc, boxcoords, cmdargs.ttf, rgb,
                           showrect=cmdargs.showrects,
                           hjust=info.get('hjust', 0.5),
                           vjust=info.get('vjust', 0.5))
    for el in extralabels:
        add_label(img, el['text'], el['x'], el['y'], cmdargs.ttf,
                  el['fontsize'], el['rgb'],
                  hjust=el.get('hjust', 0), vjust=el.get('vjust', 0))
    logger.info("Saving to: {}".format(outfile))
    img.save(outfile)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
        # Fetch command-line options.
    silent = False
    parser = argparse.ArgumentParser(
        description="Generate Thrustmaster Warthog binding pictures. "
        "For a simple example, run with the arguments '--format demo' only."
    )
    parser.add_argument(
        '--format', default="json", choices=['json', 'ed', 'demo'],
        required=True,
        help="Input format. Possible values: "
        "'json' (same format as produced by --showmapping); "
        "'ed' (Elite Dangerous .binds file); "
        "'demo' (simple demonstration)")
    parser.add_argument(
        '--input', default=None,
        help="Input file (unless 'demo' mode is used)")
    parser.add_argument(
        '--joyout', default=DEFAULT_JOYSTICK_OUTPUT,
        help="Joystick output file (default: {})".format(
            DEFAULT_JOYSTICK_OUTPUT))
    parser.add_argument(
        '--throtout', default=DEFAULT_THROTTLE_OUTPUT,
        help="Throttle output file (default: {})".format(
            DEFAULT_THROTTLE_OUTPUT))
    parser.add_argument(
        '--compout', default=DEFAULT_COMPOSITE_OUTPUT,
        help="Composite output file (default: {})".format(
            DEFAULT_COMPOSITE_OUTPUT))
    parser.add_argument(
        '--joytemplate', default=DEFAULT_JOYSTICK_TEMPLATE,
        help="Joystick template (default: {})".format(
            DEFAULT_JOYSTICK_TEMPLATE))
    parser.add_argument(
        '--throttemplate', default=DEFAULT_THROTTLE_TEMPLATE,
        help="Throttle template (default: {})".format(
            DEFAULT_THROTTLE_TEMPLATE))
    parser.add_argument(
        '--ed_tmw_stick', default=DEFAULT_ED_STICK,
        help="Elite Dangerous device name for Thrustmaster Warthog joystick "
        "(default: {})".format(DEFAULT_ED_STICK))
    parser.add_argument(
        '--ed_tmw_throttle', default=DEFAULT_ED_THROTTLE,
        help="Elite Dangerous device name for Thrustmaster Warthog throttle/"
        "control panel (default: {})".format(DEFAULT_ED_THROTTLE))
    parser.add_argument(
        '--ed_mfg_crosswind', default=DEFAULT_ED_MFG_CROSSWIND_NAME,
        help="Elite Dangerous device name for MFG Crosswind rudder pedals "
        "(default: {})".format(DEFAULT_ED_MFG_CROSSWIND_NAME))
    parser.add_argument(
        '--ed_horizons', action='store_true',
        help="Include bindings for Elite Dangerous: Horizons (lander buggy)")
    parser.add_argument(
        '--rgbanalogue', type=rgb_tuple_from_csv, default=DEFAULT_RGB_ANALOGUE,
        help="RGB colours for analogue devices (default: {})".format(
            DEFAULT_RGB_ANALOGUE))
    parser.add_argument(
        '--rgbmomentary', type=rgb_tuple_from_csv,
        default=DEFAULT_RGB_MOMENTARY,
        help="RGB colours for momentary switches (switches that deactivate "
        "when released; default: {})".format(
            DEFAULT_RGB_MOMENTARY))
    parser.add_argument(
        '--rgbsticky', type=rgb_tuple_from_csv, default=DEFAULT_RGB_STICKY,
        help="RGB colours for sticky switches (switches that keep their "
        "position when released; default: {})".format(
            DEFAULT_RGB_STICKY))
    parser.add_argument(
        '--showmapping', action='store_true',
        help="Print mapping to stdout")
    parser.add_argument(
        '--showrects', action='store_true',
        help="Debugging option: show text rectangles")
    parser.add_argument(
        '--ttf', default=DEFAULT_TRUETYPE_FILE,
        help="TrueType font file (default: {})".format(DEFAULT_TRUETYPE_FILE))
    parser.add_argument('--verbose', action='count', default=0, help="Verbose")
    args = parser.parse_args()

    assert args.input is not None or args.format == 'demo', (
        "Must specify input unless using 'demo' mode; use --help for help"
    )

    logging.basicConfig(level=logging.DEBUG if args.verbose >= 1
                        else logging.INFO)

    logger.info("Thrustmaster Warthog binding diagram generator")
    logger.info("By Rudolf Cardinal (rudolf@pobox.com), 2016-02-07")
    logger.info("Templates courtesy of rayz007, "
                "http://forums.eagle.ru/showthread.php?t=102016")
    logger.debug("args: {}".format(args))

    mapping = get_mapping(args)
    if args.showmapping:
        print(json.dumps(mapping, sort_keys=True,
                         indent=4, separators=(',', ': ')))
    make_picture(merge_dicts(mapping[TMW_STICK_NAME],
                             mapping[MFG_CROSSWIND_NAME]),
                 merge_dicts(TMW_STICK_MAP, MFG_CROSSWIND_MAP),
                 args.joytemplate, args.joyout,
                 args,
                 extralabels=CROSSWIND_EXTRA_LABELS)
    make_picture(mapping[TMW_THROTTLE_NAME], TMW_THROTTLE_MAP,
                 args.throttemplate, args.throtout,
                 args)
    composite_side_by_side(args.compout,
                           [args.throtout, args.joyout])
