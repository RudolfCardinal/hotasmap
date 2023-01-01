#!/usr/bin/env python3

"""
Image sources (see also info message):
    https://forums.eagle.ru/showthread.php?t=102016

Other's efforts:
    https://github.com/subn3t/warthog
    ... at http://subn3t.com/warthog/  -- doesn't do all the keys!

VERSION HISTORY

* 2015-02-08

  - Word wrap.

* 2015-02-07

  - Created.

* 2016-04-10

  - PyCharm code cleanup.

* 2018-01-21

  - Better documentation.

* 2020-12-27

  - Type hinting.
  - Label axes more clearly (per Windows drivers).
  - Python 3.7 requirement, for dataclass.
  - Title/subtitle.
  - Option to print blank template.
  - Script files for convenience.
  - Added demo Elite and JSON files.
  - Star Wars: Squadrons specimen (as JSON).

"""

# =============================================================================
# Imports
# =============================================================================

import argparse
from dataclasses import dataclass
from enum import Enum
import json
import logging
import os
import re
from xml.etree import ElementTree
import sys
from typing import Any, Dict, List, Literal, Optional, Tuple

from cardinal_pythonlib.argparse_func import (
    RawDescriptionArgumentDefaultsHelpFormatter,
)  # noqa
from cardinal_pythonlib.enumlike import keys_descriptions_from_enum
from PIL import (  # install with "pip install pillow" but import as PIL
    Image,
    ImageDraw,
    ImageFont,
)

log = logging.getLogger(__name__)


# =============================================================================
# Paths
# =============================================================================

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(THIS_DIR, "output")
TEMPLATE_DIR = os.path.join(THIS_DIR, "templates")


# =============================================================================
# Defaults
# =============================================================================

DEFAULT_JOYSTICK_TEMPLATE = os.path.join(
    TEMPLATE_DIR, "TEMPLATE_tmw_joystick.png"
)
DEFAULT_THROTTLE_TEMPLATE = os.path.join(
    TEMPLATE_DIR, "TEMPLATE_tmw_throttle.png"
)
DEFAULT_JOYSTICK_OUTPUT = os.path.join(OUTPUT_DIR, "output_joystick.png")
DEFAULT_THROTTLE_OUTPUT = os.path.join(OUTPUT_DIR, "output_throttle.png")
DEFAULT_COMPOSITE_OUTPUT = os.path.join(OUTPUT_DIR, "output_composite.png")

DEFAULT_TRUETYPE_FILE = "Arial.ttf"
# Slightly clearer than Arial_Bold.ttf?

DEFAULT_RGB_TITLE = "0,100,0"  # dark green
DEFAULT_RGB_ANALOGUE = "177,97,0"  # very dark orange
DEFAULT_RGB_MOMENTARY = "0,0,255"  # blue
DEFAULT_RGB_STICKY = "255,0,0"  # red
# The one that should be most visible is DEFAULT_RGB_MOMENTARY, which accounts
# for most of the switches, and which you're most likely to be hunting for in
# semi-darkness. Then, the contrast between "momentary" and "sticky" matters
# more than analogue, which is usually obvious physically.

DEFAULT_ED_STICK = "ThrustMasterWarthogJoystick"
DEFAULT_ED_THROTTLE = "ThrustMasterWarthogThrottle"
DEFAULT_ED_MFG_CROSSWIND_NAME = "16D00A38"  # always this value or not?


# =============================================================================
# Other constants
# =============================================================================


MFG_CROSSWIND_NAME = "mfg_crosswind_pedals"

RECT_OUTLINE = (0, 0, 0)
RECT_FILL = (240, 240, 240)

ANALOGUE = "~"
MOMENTARY = "."
STICKY = "+"


# =============================================================================
# Devices, with mappings to picture coordinates, Elite Dangerous switch names,
# etc.
# =============================================================================

# -----------------------------------------------------------------------------
# Thrustmaster HOTAS Warthog: joystick
# -----------------------------------------------------------------------------

TMW_STICK_NAME = "thrustmaster_warthog_joystick"
J_WIDTH = 192  # reference: TrimHat_Up
J_XWIDE = J_WIDTH + 10  # common extra width
J_HEIGHT = 55  # reference: TrimHat_Up

# Labels on left-hand side:

WEP_L = 273  # _L: left coordinate
WEP_T = 337  # _T: top coordinate

TMS_L1 = 60
TMS_L2 = 241
TMS_L3 = 416
TMS_T1 = 498
TMS_T2 = 600
TMS_T3 = 705

CMS_L1 = 60
CMS_L2 = 80
CMS_L3 = 240
CMS_L4 = 324
CMS_L5 = 420
CMS_T1 = 1042
CMS_T2 = 1144
CMS_T3 = 1249
CMS_T4 = 1260

STICK_L1 = 39
STICK_L2 = 189
STICK_L3 = 213
STICK_L4 = 377
STICK_T1 = 1375
STICK_T2 = 1592
STICK_T3 = 1604
STICK_T4 = 1710

# Labels on right-hand side:

TRIMHAT_L1 = 909
TRIMHAT_L2 = 940
TRIMHAT_L3 = 1146
TRIMHAT_L4 = 1350
TRIMHAT_L5 = 1375
TRIMHAT_T1 = 103
TRIMHAT_T2 = 164
TRIMHAT_T3 = 250
TRIMHAT_T4 = 326
TRIMHAT_T5 = 397

MMC_L = 1222
MMC_T = 556

DMS_L1 = 1003
DMS_L2 = 1183
DMS_L3 = 1360
DMS_T1 = 727
DMS_T2 = 830
DMS_T3 = 935

GUNGROUP_L1 = 723
GUNGROUP_L2 = 770
GUNGROUP_L3 = 1308
GUNGROUP_L4 = 1342
GUNGROUP_T1 = 1738
GUNGROUP_T2 = 1863
GUNGROUP_T3 = 1868
GUNGROUP_T4 = 1982

TMW_STICK_MAP = {
    # Dictionary attributes:
    #   l, t = left, top edge of text box
    #   w, h = width, height of text box
    #   ed = Elite Dangerous key name
    #   type = '~' analogue, '.' momentary switch, '+' sticky switch
    # overall image size is 1625 x 2201
    "Stick_Forward": dict(
        l=STICK_L3,
        t=STICK_T1,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_YAxis",
        type=ANALOGUE,
    ),
    "Stick_Backward": dict(
        l=STICK_L2,
        t=STICK_T4,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_YAxis",
        type=ANALOGUE,
    ),
    "Stick_Left": dict(
        l=STICK_L1,
        t=STICK_T2,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_XAxis",
        type=ANALOGUE,
    ),
    "Stick_Right": dict(
        l=STICK_L4,
        t=STICK_T3,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_XAxis",
        type=ANALOGUE,
    ),
    "TrimHat_Up": dict(
        l=TRIMHAT_L3,
        t=TRIMHAT_T1,
        w=J_WIDTH,
        h=J_HEIGHT,
        ed="Joy_POV1Up",
        type=MOMENTARY,
    ),
    "TrimHat_Left": dict(
        l=TRIMHAT_L1,
        t=TRIMHAT_T3,
        w=J_WIDTH,
        h=J_HEIGHT,
        ed="Joy_POV1Left",
        type=MOMENTARY,
    ),
    "TrimHat_Right": dict(
        l=TRIMHAT_L5,
        t=TRIMHAT_T3,
        w=J_WIDTH,
        h=J_HEIGHT,
        ed="Joy_POV1Right",
        type=MOMENTARY,
    ),
    "TrimHat_Down": dict(
        l=TRIMHAT_L3,
        t=TRIMHAT_T5,
        w=J_WIDTH,
        h=J_HEIGHT,
        ed="Joy_POV1Down",
        type=MOMENTARY,
    ),
    # Not sure these are actually valid
    "TrimHat_UpLeft": dict(l=TRIMHAT_L2, t=TRIMHAT_T2, w=J_WIDTH, h=J_HEIGHT),
    "TrimHat_UpRight": dict(l=TRIMHAT_L4, t=TRIMHAT_T2, w=J_WIDTH, h=J_HEIGHT),
    "TrimHat_DownLeft": dict(
        l=TRIMHAT_L2, t=TRIMHAT_T4, w=J_WIDTH, h=J_HEIGHT
    ),
    "TrimHat_DownRight": dict(
        l=TRIMHAT_L4, t=TRIMHAT_T4, w=J_WIDTH, h=J_HEIGHT
    ),
    "S1_Trigger_FirstStage": dict(
        l=GUNGROUP_L1,
        t=GUNGROUP_T1,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_1",
        type=MOMENTARY,
    ),
    "S2_WeaponsRelease": dict(
        l=WEP_L,
        t=WEP_T,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_2",
        type=MOMENTARY,
    ),
    "S3_NSB": dict(  # nosewheel steering button
        l=GUNGROUP_L4,
        t=GUNGROUP_T2,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_3",
        type=MOMENTARY,
    ),
    "S4_PinkieLever": dict(
        l=GUNGROUP_L3,
        t=GUNGROUP_T4,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_4",
        type=MOMENTARY,
    ),
    "S5_MMC": dict(  # master mode control
        l=MMC_L,
        t=MMC_T,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_5",
        type=MOMENTARY,
    ),
    "S6_Trigger_SecondStage": dict(
        l=GUNGROUP_L2,
        t=GUNGROUP_T3,
        w=J_XWIDE,
        h=J_HEIGHT,
        ed="Joy_6",
        type=MOMENTARY,
    ),
    # Target management switch
    "S7_TMS_Up": dict(
        l=TMS_L2, t=TMS_T1, w=J_XWIDE, h=J_HEIGHT, ed="Joy_7", type=MOMENTARY
    ),
    "S8_TMS_Right": dict(
        l=TMS_L3, t=TMS_T2, w=J_WIDTH, h=J_HEIGHT, ed="Joy_8", type=MOMENTARY
    ),
    "S9_TMS_Down": dict(
        l=TMS_L2, t=TMS_T3, w=J_XWIDE, h=J_HEIGHT, ed="Joy_9", type=MOMENTARY
    ),
    "S10_TMS_Left": dict(
        l=TMS_L1, t=TMS_T2, w=J_XWIDE, h=J_HEIGHT, ed="Joy_10", type=MOMENTARY
    ),
    # Data management switch
    "S11_DMS_Up": dict(
        l=DMS_L2, t=DMS_T1, w=J_XWIDE, h=J_HEIGHT, ed="Joy_11", type=MOMENTARY
    ),
    "S12_DMS_Right": dict(
        l=DMS_L3, t=DMS_T2, w=J_WIDTH, h=J_HEIGHT, ed="Joy_12", type=MOMENTARY
    ),
    "S13_DMS_Down": dict(
        l=DMS_L2, t=DMS_T3, w=J_XWIDE, h=J_HEIGHT, ed="Joy_13", type=MOMENTARY
    ),
    "S14_DMS_Left": dict(
        l=DMS_L1, t=DMS_T2, w=J_XWIDE, h=J_HEIGHT, ed="Joy_14", type=MOMENTARY
    ),
    # Countermeasures management switch
    "S15_CMS_Forward": dict(
        l=CMS_L3, t=CMS_T1, w=J_XWIDE, h=J_HEIGHT, ed="Joy_15", type=MOMENTARY
    ),
    "S16_CMS_Right": dict(
        l=CMS_L5, t=CMS_T2, w=J_WIDTH, h=J_HEIGHT, ed="Joy_16", type=MOMENTARY
    ),
    "S17_CMS_Backward": dict(
        l=CMS_L2, t=CMS_T3, w=J_XWIDE, h=J_HEIGHT, ed="Joy_17", type=MOMENTARY
    ),
    "S18_CMS_Left": dict(
        l=CMS_L1, t=CMS_T2, w=J_XWIDE, h=J_HEIGHT, ed="Joy_18", type=MOMENTARY
    ),
    "S19_CMS_Press": dict(
        l=CMS_L4, t=CMS_T4, w=J_XWIDE, h=J_HEIGHT, ed="Joy_19", type=MOMENTARY
    ),
}

TMW_STICK_EXTRA_LABELS = [
    dict(
        text="X axis",
        x=475,
        y=1525 + J_HEIGHT / 2,
        fontsize=20,
        rgb=(0, 0, 0),
        hjust=1,
        vjust=0.5,
    ),
    dict(
        text="Y axis",
        x=350,
        y=1415 + J_HEIGHT / 2,
        fontsize=20,
        rgb=(0, 0, 0),
        hjust=1,
        vjust=0.5,
    ),
]


# -----------------------------------------------------------------------------
# Thrustmaster HOTAS Warthog: throttle
# -----------------------------------------------------------------------------

TMW_THROTTLE_NAME = "thrustmaster_warthog_throttle"
T_WIDTH = 162  # reference: S31_LeftEngineOperateUp
T_HEIGHT = 39  # reference: S31_LeftEngineOperateUp
T_IDLE_WIDTH = 114
T_IDLE_HEIGHT = 22

# Labels on the left-hand side of the box:

FLAPS_L = 205
FLAPS_T1 = 738
FLAPS_T2 = 792

EAC_L = 170
EAC_T = 1040

RDRALT_L = 345
RDRALT_T = 1230

# Labels on the right-hand side of the box:

FUEL_L1 = 650
FUEL_L2 = 875
FUEL_T = 67

ENG_L = 1339
ENG_T1 = 351
ENG_T2 = 408
ENG_T3 = 467
ENG_T4 = 525

APU_L = 1232
APU_T = 590

THFRICT_L = 1358
THFRICT_T = 692

GEARWARN_L = 1330
GEARWARN_T = 788

APILOT_L1 = 1036
APILOT_L2 = 1355
APILOT_T1 = 987
APILOT_T2 = EAC_T
APILOT_T3 = RDRALT_T

# Throttle, left:

COOLIE_L1 = 377
COOLIE_L2 = 395
COOLIE_L3 = 550
COOLIE_L4 = 710
COOLIE_L5 = 725
# Not exactly aligned, but very close:
COOLIE_T1 = 1315
COOLIE_T2 = 1367
COOLIE_T3 = 1425
COOLIE_T4 = 1482
COOLIE_T5 = 1536

THUMBHAT_L1 = 113
THUMBHAT_L2 = 125
THUMBHAT_L3 = 228
THUMBHAT_L4 = 280
THUMBHAT_L5 = 342
THUMBHAT_W = 130
THUMBHAT_NARROW = THUMBHAT_W - 7
THUMBHAT_T1 = 1565
THUMBHAT_T2 = 1630
THUMBHAT_T3 = 1697
THUMBHAT_T4 = 1704
THUMBHAT_H = 35

BRAKEGROUP_L = 227
BRAKEGROUP_W = 148
BRAKEGROUP_T1 = 1756
BRAKEGROUP_T2 = 1801
BRAKEGROUP_T3 = 1854
BRAKEGROUP_T4 = 1900
BRAKEGROUP_T5 = 1953
BRAKEGROUP_T6 = 1999
BRAKEGROUP_H = 35

# Throttle, right:

SLEW_L1 = 954
SLEW_L2 = 1056
SLEW_L3 = 1156
SLEW_T1 = 1330
SLEW_T2 = 1440
SLEW_T3 = 1567
SLEW_MOUSE_W = J_XWIDE
SLEW_MOUSE_H = J_HEIGHT

THBUT_L = 1346
THBUT_T = 1522

PINKY_L = 1392
PINKY_T1 = 1897
PINKY_T2 = 1960

# Throttle, bottom:

THLEVER_L1 = 580
THLEVER_L2 = 1115
THLEVER_W = J_XWIDE
THLEVER_T = 2130
THLEVER_H = J_HEIGHT

TMW_THROTTLE_MAP = {
    # overall image size is 1625 x 2201
    "LeftThrottle": dict(
        l=THLEVER_L2,
        t=THLEVER_T,
        w=THLEVER_W,
        h=THLEVER_H,
        ed="Joy_RZAxis",
        type=ANALOGUE,
    ),
    "RightThrottle": dict(
        l=THLEVER_L1,
        t=THLEVER_T,
        w=THLEVER_W,
        h=THLEVER_H,
        ed="Joy_ZAxis",
        type=ANALOGUE,
    ),
    "CoolieSwitchUp": dict(
        l=COOLIE_L3,
        t=COOLIE_T1,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_POV1Up",
        type=MOMENTARY,
    ),
    "CoolieSwitchDown": dict(
        l=COOLIE_L3,
        t=COOLIE_T5,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_POV1Down",
        type=MOMENTARY,
    ),
    "CoolieSwitchLeft": dict(
        l=COOLIE_L5,
        t=COOLIE_T3,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_POV1Left",
        type=MOMENTARY,
    ),
    "CoolieSwitchRight": dict(
        l=COOLIE_L1,
        t=COOLIE_T3,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_POV1Right",
        type=MOMENTARY,
    ),
    "CoolieSwitchUpLeft": dict(
        l=COOLIE_L4, t=COOLIE_T2, w=T_WIDTH, h=T_HEIGHT
    ),
    "CoolieSwitchUpRight": dict(
        l=COOLIE_L2, t=COOLIE_T2, w=T_WIDTH, h=T_HEIGHT
    ),
    "CoolieSwitchDownLeft": dict(
        l=COOLIE_L4, t=COOLIE_T4, w=T_WIDTH, h=T_HEIGHT
    ),
    "CoolieSwitchDownRight": dict(
        l=COOLIE_L2, t=COOLIE_T4, w=T_WIDTH, h=T_HEIGHT
    ),
    "ThrottleFrictionControl": dict(
        l=THFRICT_L,
        t=THFRICT_T,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_UAxis",
        type=ANALOGUE,
    ),
    "SlewControl_LeftRight": dict(
        l=SLEW_L3,
        t=SLEW_T2,
        w=SLEW_MOUSE_W,
        h=SLEW_MOUSE_H,
        ed="Joy_XAxis",
        type=ANALOGUE,
    ),
    "SlewControl_UpDown": dict(
        l=SLEW_L2,
        t=SLEW_T1,
        w=SLEW_MOUSE_W,
        h=SLEW_MOUSE_H,
        ed="Joy_YAxis",
        type=ANALOGUE,
    ),
    "S1_SlewControl_Press": dict(
        l=SLEW_L1, t=SLEW_T3, w=T_WIDTH, h=T_HEIGHT, ed="Joy_1", type=MOMENTARY
    ),
    "S2_ThumbHat_Press": dict(
        l=THUMBHAT_L4,
        t=THUMBHAT_T4,
        w=THUMBHAT_W,
        h=THUMBHAT_H,
        ed="Joy_2",
        type=MOMENTARY,
    ),
    "S3_ThumbHat_Up": dict(
        l=THUMBHAT_L3,
        t=THUMBHAT_T1,
        w=THUMBHAT_W,
        h=THUMBHAT_H,
        ed="Joy_3",
        type=MOMENTARY,
    ),
    "S4_ThumbHat_Forward": dict(
        l=THUMBHAT_L5,
        t=THUMBHAT_T2,
        w=THUMBHAT_NARROW,
        h=THUMBHAT_H,
        ed="Joy_4",
        type=MOMENTARY,
    ),
    "S5_ThumbHat_Down": dict(
        l=THUMBHAT_L2,
        t=THUMBHAT_T3,
        w=THUMBHAT_W,
        h=THUMBHAT_H,
        ed="Joy_5",
        type=MOMENTARY,
    ),
    "S6_ThumbHat_Backward": dict(
        l=THUMBHAT_L1,
        t=THUMBHAT_T2,
        w=THUMBHAT_W,
        h=THUMBHAT_H,
        ed="Joy_6",
        type=MOMENTARY,
    ),
    "S7_Speedbrake_Forward": dict(
        l=BRAKEGROUP_L,
        t=BRAKEGROUP_T1,
        w=BRAKEGROUP_W,
        h=BRAKEGROUP_H,
        ed="Joy_7",
        type=STICKY,
    ),
    "S8_Speedbrake_Backward": dict(
        l=BRAKEGROUP_L,
        t=BRAKEGROUP_T2,
        w=BRAKEGROUP_W,
        h=BRAKEGROUP_H,
        ed="Joy_8",
        type=MOMENTARY,
    ),
    "S9_BoatSwitch_Forward": dict(
        l=BRAKEGROUP_L,
        t=BRAKEGROUP_T3,
        w=BRAKEGROUP_W,
        h=BRAKEGROUP_H,
        ed="Joy_9",
        type=STICKY,
    ),
    "S10_BoatSwitch_Backward": dict(
        l=BRAKEGROUP_L,
        t=BRAKEGROUP_T4,
        w=BRAKEGROUP_W,
        h=BRAKEGROUP_H,
        ed="Joy_10",
        type=STICKY,
    ),
    "S11_ChinaHat_Forward": dict(
        l=BRAKEGROUP_L,
        t=BRAKEGROUP_T5,
        w=BRAKEGROUP_W,
        h=BRAKEGROUP_H,
        ed="Joy_11",
        type=MOMENTARY,
    ),
    "S12_ChinaHat_Backward": dict(
        l=BRAKEGROUP_L,
        t=BRAKEGROUP_T6,
        w=BRAKEGROUP_W,
        h=BRAKEGROUP_H,
        ed="Joy_12",
        type=MOMENTARY,
    ),
    "S13_PinkieSwitch_Forward": dict(
        l=PINKY_L, t=PINKY_T1, w=T_WIDTH, h=T_HEIGHT, ed="Joy_13", type=STICKY
    ),
    "S14_PinkieSwitch_Backward": dict(
        l=PINKY_L, t=PINKY_T2, w=T_WIDTH, h=T_HEIGHT, ed="Joy_14", type=STICKY
    ),
    "S15_LeftThrottleButton": dict(
        l=THBUT_L,
        t=THBUT_T,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_15",
        type=MOMENTARY,
    ),
    "S16_LeftEngineFuelFlow": dict(
        l=FUEL_L1, t=FUEL_T, w=T_WIDTH, h=T_HEIGHT, ed="Joy_16", type=STICKY
    ),
    "S17_RightEngineFuelFlow": dict(
        l=FUEL_L2, t=FUEL_T, w=T_WIDTH, h=T_HEIGHT, ed="Joy_17", type=STICKY
    ),
    "S18_LeftEngineOperateDown": dict(
        l=ENG_L, t=ENG_T2, w=T_WIDTH, h=T_HEIGHT, ed="Joy_18", type=STICKY
    ),
    "S19_RightEngineOperateDown": dict(
        l=ENG_L, t=ENG_T4, w=T_WIDTH, h=T_HEIGHT, ed="Joy_19", type=STICKY
    ),
    "S20_APUStart": dict(  # APU = auxiliary power unit
        l=APU_L, t=APU_T, w=T_WIDTH, h=T_HEIGHT, ed="Joy_20", type=STICKY
    ),
    "S21_LandingGearWarningSilence": dict(
        l=GEARWARN_L,
        t=GEARWARN_T,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_21",
        type=MOMENTARY,
    ),
    "S22_FlapsUp": dict(
        l=FLAPS_L, t=FLAPS_T1, w=T_WIDTH, h=T_HEIGHT, ed="Joy_22", type=STICKY
    ),
    "S23_FlapsDown": dict(
        l=FLAPS_L, t=FLAPS_T2, w=T_WIDTH, h=T_HEIGHT, ed="Joy_23", type=STICKY
    ),
    "S24_EAC": dict(  # Enhanced Attitude Control
        l=EAC_L, t=EAC_T, w=T_WIDTH, h=T_HEIGHT, ed="Joy_24", type=STICKY
    ),
    "S25_RadarAltimeter": dict(
        l=RDRALT_L, t=RDRALT_T, w=T_WIDTH, h=T_HEIGHT, ed="Joy_25", type=STICKY
    ),
    "S26_AutopilotEngageDisengage": dict(
        l=APILOT_L1,
        t=APILOT_T3,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_26",
        type=MOMENTARY,
    ),
    "S27_AutopilotMode_Up": dict(
        l=APILOT_L2,
        t=APILOT_T1,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_27",
        type=STICKY,
    ),
    "S28_AutopilotMode_Down": dict(
        l=APILOT_L2,
        t=APILOT_T2,
        w=T_WIDTH,
        h=T_HEIGHT,
        ed="Joy_28",
        type=STICKY,
    ),
    "S29_RightEngineIdle": dict(
        l=569, t=713, w=T_IDLE_WIDTH, h=T_IDLE_HEIGHT, ed="Joy_29", type=STICKY
    ),
    "S30_LeftEngineIdle": dict(
        l=787, t=713, w=T_IDLE_WIDTH, h=T_IDLE_HEIGHT, ed="Joy_30", type=STICKY
    ),
    "S31_LeftEngineOperateUp": dict(
        l=ENG_L, t=ENG_T1, w=T_WIDTH, h=T_HEIGHT, ed="Joy_31", type=MOMENTARY
    ),
    "S32_RightEngineOperateUp": dict(
        l=ENG_L, t=ENG_T3, w=T_WIDTH, h=T_HEIGHT, ed="Joy_32", type=MOMENTARY
    ),
}

TMW_THROTTLE_EXTRA_LABELS = [
    dict(
        text="(Z axis)",  # right throttle (shown on the left)
        x=565,
        y=2115,
        fontsize=20,
        rgb=(0, 0, 0),
        hjust=1,
        vjust=0.5,
    ),
    dict(
        text="(Z rotation)",  # left throttle (shown on the right)
        x=1320,
        y=2115,
        fontsize=20,
        rgb=(0, 0, 0),
        hjust=0,
        vjust=0.5,
    ),
]


# -----------------------------------------------------------------------------
# MFG Crosswind rudder pedals
# -----------------------------------------------------------------------------

PEDAL_LABEL_L = 300
PEDAL_L = 325
PEDAL_T1 = 1850
PEDAL_T2 = 1925
PEDAL_T3 = 2000

MFG_CROSSWIND_MAP = {
    # These are specials from the MFG Crosswind:
    "Rudder": dict(
        l=PEDAL_L,
        t=PEDAL_T1,
        w=J_XWIDE,
        h=J_HEIGHT,
        hjust=0,
        ed="Joy_RZAxis",
        type=ANALOGUE,
    ),
    "LeftFootbrake": dict(
        l=PEDAL_L,
        t=PEDAL_T2,
        w=J_XWIDE,
        h=J_HEIGHT,
        hjust=0,
        ed="Joy_XAxis",
        type=ANALOGUE,
    ),
    "RightFootbrake": dict(
        l=PEDAL_L,
        t=PEDAL_T3,
        w=J_XWIDE,
        h=J_HEIGHT,
        hjust=0,
        ed="Joy_YAxis",
        type=ANALOGUE,
    ),
}

CROSSWIND_EXTRA_LABELS = [
    dict(
        text="Pedals: Rudder\n(Z rotation, L←|→R)",
        x=PEDAL_LABEL_L,
        y=PEDAL_T1 + J_HEIGHT / 2,
        fontsize=20,
        rgb=(0, 0, 0),
        hjust=1,
        vjust=0.5,
    ),
    dict(
        text="Pedals: Left footbrake\n(X axis)",
        x=PEDAL_LABEL_L,
        y=PEDAL_T2 + J_HEIGHT / 2,
        fontsize=20,
        rgb=(0, 0, 0),
        hjust=1,
        vjust=0.5,
    ),
    dict(
        text="Pedals: Right footbrake\n(Y axis)",
        x=PEDAL_LABEL_L,
        y=PEDAL_T3 + J_HEIGHT / 2,
        fontsize=20,
        rgb=(0, 0, 0),
        hjust=1,
        vjust=0.5,
    ),
]


# =============================================================================
# Map E:D labels to human
# =============================================================================

ED_LABEL_MAP = {
    "AheadThrust_Landing": "Ldg/Thrust fwd/back",
    "AheadThrust": "Thrust fwd/back",
    "BackwardKey": "Backward",
    "BackwardThrustButton_Landing": "Ldg/Thrust back",
    "BackwardThrustButton": "Thrust back",
    "CamPitchAxis": "Cam. pitch",
    "CamPitchDown": "Cam. pitch down",
    "CamPitchUp": "Cam. pitch up",
    "CamTranslateBackward": "Cam. backward",
    "CamTranslateDown": "Cam. xlate down",
    "CamTranslateForward": "Cam. forward",
    "CamTranslateLeft": "Cam. xlate L",
    "CamTranslateRight": "Cam. xlate R",
    "CamTranslateUp": "Cam. xlate up",
    "CamTranslateXAxis": "Cam. xlate L/R",
    "CamTranslateYAxis": "Cam. xlate fwd/back",  # *** check
    "CamTranslateZAxis": "Cam. xlate up/down",
    "CamTranslateZHold": "Cam. xlate Z hold",
    "CamYawAxis": "Cam. yaw",
    "CamYawLeft": "Cam. yaw L",
    "CamYawRight": "Cam. yaw R",
    "CamZoomAxis": "Cam. zoom",
    "CamZoomIn": "Cam. zoom in",
    "CamZoomOut": "Cam. zoom out",
    "CycleFireGroupNext": "Next firegroup",
    "CycleFireGroupPrevious": "Prev. firegroup",
    "CycleNextHostileTarget": "Next hostile target",
    "CycleNextPanel": "UI next panel",
    "CycleNextSubsystem": "Next target subsyst.",
    "CycleNextTarget": "Next target",
    "CyclePreviousHostileTarget": "Prev. hostile target",
    "CyclePreviousPanel": "UI prev. panel",
    "CyclePreviousSubsystem": "Prev. target subsyst.",
    "CyclePreviousTarget": "Prev. target",
    "DeployHardpointToggle": "Hardpoints ±",
    "DeployHeatSink": "Heatsink",
    "DisableRotationCorrectToggle": "Rotat. correction",
    "DownThrustButton_Landing": "Ldg/Thrust down",
    "DownThrustButton": "Thrust down",
    "EjectAllCargo": "Eject cargo",
    "FireChaffLauncher": "Chaff",
    "FocusCommsPanel": "UI COMMS panel",
    "FocusLeftPanel": "UI LEFT panel",
    "FocusRadarPanel": "UI RADAR panel",
    "FocusRightPanel": "UI RIGHT panel",
    "ForwardKey": "Forward",
    "ForwardThrustButton_Landing": "Ldg/Thrust fwd",
    "GalaxyMapOpen": "Galaxy map",
    "HeadLookPitchAxisRaw": "Headlook up/down",
    "HeadLookPitchDown": "Headlook down",
    "HeadLookPitchUp": "Headlook up",
    "HeadLookReset": "Reset headlook",
    "HeadLookToggle": "Headlook ±",
    "HeadLookYawAxis": "Headlook L/R",
    "HeadLookYawLeft": "Headlook L",
    "HeadLookYawRight": "Headlook R",
    "HMDReset": "Reset VR orientation",  # *** I think
    "HyperSuperCombination": "Frame Shift Drive ±",
    "IncreaseEnginesPower": "Pwr→ENGINES",
    "IncreaseSystemsPower": "Pwr→SYSTEMS",
    "IncreaseWeaponsPower": "Pwr→WEAPONS",
    "LandingGearToggle": "Landing gear ±",
    "LateralThrustAlternate": "Lateral thrust (ALT)",
    "LateralThrust_Landing": "Ldg/Lateral thrust",
    "LateralThrustRaw": "Lateral thrust",
    "LeftThrustButton_Landing": "Ldg/Thrust L",
    "LeftThrustButton": "Thrust L",
    "MicrophoneMute": "Mic. mute",
    "OrbitLinesToggle": "Orbit lines ±",
    "PhotoCameraToggle": "Camera view ±",
    "PitchAxisAlternate": "Pitch (ALT)",
    "PitchAxis_Landing": "Ldg/Pitch",
    "PitchAxisRaw": "Pitch",
    "PitchDownButton_Landing": "Ldg/Pitch down",
    "PitchDownButton": "Pitch down",
    "PitchUpButton_Landing": "Ldg/Pitch up",
    "PitchUpButton": "Pitch up",
    "PrimaryFire": "Fire 1",
    "QuickCommsPanel": "Quick comms",
    "RadarDecreaseRange": "Radar +",
    "RadarIncreaseRange": "Radar –",
    "RadarRangeAxis": "Radar range",
    "ResetPowerDistribution": "Balance pwr distrib.",
    "RightThrustButton_Landing": "Ldg/Thrust R",
    "RightThrustButton": "Thrust R",
    "RollAxisAlternate": "Roll (ALT)",
    "RollAxis_Landing": "Ldg/Roll",
    "RollAxisRaw": "Roll",
    "RollLeftButton_Landing": "Ldg/Roll L",
    "RollLeftButton": "Roll L",
    "RollRightButton_Landing": "Ldg/Roll R",
    "RollRightButton": "Roll R",
    "SecondaryFire": "Fire 2",
    "SelectHighestThreat": "Highest threat",
    "SelectTargetsTarget": "Target's target",
    "SelectTarget": "Target ahead",
    "SetSpeed100": "Speed 100%",
    "SetSpeed25": "Speed 25%",
    "SetSpeed50": "Speed 50%",
    "SetSpeed75": "Speed 75%",
    "SetSpeedMinus100": "Speed –100%",
    "SetSpeedMinus25": "Speed –25%",
    "SetSpeedMinus50": "Speed –50%",
    "SetSpeedMinus75": "Speed –75%",
    "SetSpeedZero": "Speed 0%",
    "ShipSpotLightToggle": "Lights ±",
    "ShowPGScoreSummaryInput": "ShowPGScoreSummaryInput",  # *** ??
    "SystemMapOpen": "System map",
    "TargetNextRouteSystem": "Next system in route",
    "TargetWingman0": "Wingman 1",
    "TargetWingman1": "Wingman 2",
    "TargetWingman2": "Wingman 3",
    "ThrottleAxis": "Throttle",
    "ToggleButtonUpInput": "Silent running",
    "ToggleCargoScoop": "Cargo scoop",
    "ToggleFlightAssist": "Flight Assist",
    "ToggleReverseThrottleInput": "Reverse throttle",
    "UI_Back": "UI back",
    "UI_Down": "UI down",
    "UIFocus": "UI focus",
    "UI_Left": "UI left",
    "UI_Right": "UI right",
    "UI_Select": "UI select",
    "UI_Up": "UI up",
    "UpThrustButton_Landing": "Ldg/Thrust up",
    "UpThrustButton": "Thrust up",
    "UseAlternateFlightValuesToggle": "Toggle ALT flight controls",
    "UseBoostJuice": "Engine boost",
    "UseShieldCell": "Shield cell",
    "VerticalThrustAlternate": "Vertical thrust (ALT)",
    "VerticalThrust_Landing": "Ldg/Vertical thrust",
    "VerticalThrustRaw": "Vertical thrust",
    "WingNavLock": "Wingman nav lock",
    "YawAxisRaw": "Yaw",
    "YawLeftButton_Landing": "Ldg/Yaw L",
    "YawLeftButton": "Yaw L",
    "YawRightButton_Landing": "Ldg/Yaw R",
    "YawRightButton": "Yaw R",
    # Those for E:D Horizons surface buggy, below, are guesswork.
    # SRV = surface reconnaissance vehicle
    "AutoBreakBuggyButton": "SRV Handbrake",  # unsure
    "BuggyPitchAxis": "SRV Pitch",
    "BuggyPrimaryFireButton": "SRV Fire 1",
    "BuggyRollAxisRaw": "SRV Roll",
    "BuggySecondaryFireButton": "SRV Fire 2",
    "BuggyToggleReverseThrottleInput": "SRV Reverse throttle",
    "BuggyTurretPitchDownButton": "SRV Turret down",
    "BuggyTurretPitchUpButton": "SRV Turret up",
    "BuggyTurretYawLeftButton": "SRV Turret L",
    "BuggyTurretYawRightButton": "SRV Turret R",
    "DriveSpeedAxis": "SRV Speed",
    "HeadlightsBuggyButton": "SRV Headlights ±",
    "SelectTarget_Buggy": "SRV Target ahead",
    "SteeringAxis": "SRV Steering",
    "ToggleBuggyTurretButton": "SRV Toggle turret",
    "ToggleDriveAssist": "SRV Drive Assist",
    "VerticalThrustersButton": "SRV Vertical Thrusters",
}
ED_HORIZONS = [  # Labels to ignore for now
    # Probably from E:D Horizons:
    "AutoBreakBuggyButton",
    "BuggyPitchAxis",
    "BuggyPrimaryFireButton",
    "BuggyRollAxisRaw",
    "BuggySecondaryFireButton",
    "BuggyToggleReverseThrottleInput",
    "BuggyTurretPitchDownButton",
    "BuggyTurretPitchUpButton",
    "BuggyTurretYawLeftButton",
    "BuggyTurretYawRightButton",
    "DriveSpeedAxis",
    "HeadlightsBuggyButton",
    "SelectTarget_Buggy",
    "SteeringAxis",
    "ToggleBuggyTurretButton",
    "ToggleDriveAssist",
    # Unsure:
    "VerticalThrustersButton",
]


# =============================================================================
# Helper functions: language
# =============================================================================


def merge_dicts(*args) -> Dict:
    """
    Creates a new dictionary that merges those passed as arguments.
    """
    if not args:
        return {}
    d = args[0].copy()
    for extra in args[1:]:
        d.update(extra)
    return d


def rgb_tuple_from_csv(text: str) -> Tuple[int]:
    """
    Returns a three-valued tuple, each in the range 0-255, from comma-
    separated text.
    """
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

RE_WHITESPACE = re.compile(r"(\s+)")
FONT_CACHE = {}
CHAR_WIDTH_CACHE = {}


def word_wrap(text: str, width: int, font: ImageFont) -> List[str]:
    """
    Word wrap function / algorithm for wrapping text using proportional (versus
    fixed-width) fonts.

    `text`: a string of text to wrap
    `width`: the width in pixels to wrap to
    `extent_func`: a function that returns a (w, h) tuple given any string, to
                   specify the size (text extent) of the string when rendered.
                   the algorithm only uses the width.

    Returns a list of strings, one for each line after wrapping.

    Based on
    https://code.activestate.com/recipes/577946-word-wrap-for-proportional-fonts/
    ... but updated for Python 3, and using a program-wide (rather than
    a function-local) font/character-size cache, which speeds it up a lot.

    """  # noqa
    lines = []
    pattern = RE_WHITESPACE
    lookup = dict((c, get_char_width(c, font)) for c in set(text))
    # ... looks up with width of each character
    for line in text.splitlines():
        tokens = pattern.split(line)
        tokens.append("")
        widths = [sum(lookup[c] for c in token) for token in tokens]
        start, total = 0, 0
        for index in range(0, len(tokens), 2):
            if total + widths[index] > width:
                end = index + 2 if index == start else index
                lines.append("".join(tokens[start:end]))
                start, total = end, 0
                if end == index + 2:
                    continue
            total += widths[index] + widths[index + 1]
        if start < len(tokens):
            lines.append("".join(tokens[start:]))
    lines = [line.strip() for line in lines]
    return lines or [""]


def word_wrap_2(text: str, width: int, font: ImageFont) -> str:
    """
    As for :func:`word_wrap` but returns a single wrapped string.

    """
    text = " ".join(text.split("\n"))
    lines = word_wrap(text, width, font)
    wrapped = "\n".join(lines)
    # logger.debug("word_wrap_2: {} -> {}".format(repr(text), repr(wrapped)))
    return wrapped


def get_font(ttf: str, fontsize: float) -> ImageFont:
    """
    Loads a font.
    Makes the error message clearer if we fail.
    Also caches the fonts.
    """
    if (ttf, fontsize) in FONT_CACHE:
        return FONT_CACHE[(ttf, fontsize)]
    try:
        font = ImageFont.truetype(ttf, fontsize)
    except Exception:
        log.error("Failed to load font!")
        raise
    FONT_CACHE[(ttf, fontsize)] = font
    return font


def get_char_width(c: str, font: ImageFont) -> int:
    """
    Caches character widths for a font.
    """
    if (c, font) in CHAR_WIDTH_CACHE:
        return CHAR_WIDTH_CACHE[(c, font)]
    width = font.getsize(c)[0]
    CHAR_WIDTH_CACHE[(c, font)] = width
    return width


def get_align_from_hjust(hjust: float) -> Literal["left", "center", "right"]:
    """
    Maps 0 -> 'left', 0.5 -> 'center', 1 -> 'right'
    ... and in-between things get nudged to the nearest of those three.
    """
    if hjust <= 0.25:
        return "left"
    elif hjust >= 0.75:
        return "right"
    return "center"


def composite_side_by_side(joinedfilename: str, filenames: List[str]) -> None:
    """
    Creates a composite image (on disk) of two or more images (specified by
    their filenames) side-by-side.
    """
    log.info("Compositing {} -> {}".format(filenames, joinedfilename))
    images = [Image.open(f) for f in filenames]
    width = sum(i.size[0] for i in images)
    height = max(i.size[1] for i in images)
    log.debug("width={}, height={}".format(width, height))
    joined = Image.new("RGB", (width, height))
    x = 0
    for i in images:
        log.debug("pasting at x={}".format(x))
        joined.paste(i, (x, 0))
        x += i.size[0]
    joined.save(joinedfilename)


def justify_to_point(
    point: float, itemsize: float, just: float = 0.0
) -> float:
    """
    Args:
        point:
            align to this coordinate
        itemsize:
            size of the item we are aligning
        just:
            How should we align?
            - 0 = left/top
            - 0.5 = centre
            - 1 = right/bottom

    Returns:
        float: starting coordinate of the item (top or left)

    Note:

    - x axis is left-to-right (and justification 0-1 is left-to-right)
    - y axis is top-to-bottom (and justification 0-1 is top-to-bottom)
    - ... so we can treat them equivalently.
    """
    return point - itemsize * just


def justify_to_box(
    boxstart: float, boxsize: float, itemsize: float, just: float = 0.0
) -> float:
    """
    Justifies, similarly, but within a box.
    """
    return boxstart + (boxsize - itemsize) * just


def add_label(
    img: Image,
    text: str,
    x: int,
    y: int,
    ttf: str,
    fontsize: float,
    rgb: Tuple[int, int, int],
    hjust: float = 0,
    vjust: float = 0,
) -> None:
    """
    Adds a label to an image.
    """
    draw = ImageDraw.Draw(img)
    font = get_font(ttf, fontsize)
    w, h = draw.textsize(text, font)
    x = justify_to_point(x, w, hjust)
    y = justify_to_point(y, h, vjust)
    draw.multiline_text(
        (x, y), text, rgb, font=font, align=get_align_from_hjust(hjust)
    )


def add_boxed_text(
    img: Image,
    text: str,
    boxcoords: Tuple[int, int, int, int],
    ttf: str,
    rgb: Tuple[int, int, int],
    showrect: bool = False,
    hjust: float = 0.5,
    vjust: float = 0.5,
    wrap: bool = False,
    font_trial_step_size: int = 5,
) -> None:
    """
    Adds text to an image, within a notional rectangle.
    """
    log.debug(
        "add_boxed_text: text={}, boxcoords={}".format(
            repr(text), repr(boxcoords)
        )
    )
    if not text:
        return
    draw = ImageDraw.Draw(img)
    boxleft, boxtop, boxwidth, boxheight = boxcoords
    base_fontsize = 16
    if wrap:
        # Tricky.
        # Start with an arbitrary font size.
        # Wrap (to box width) and calculate size.
        # If either width or height is exceeded, drop down.
        # If neither is, record this font size and increase.
        # If we end up retrying one that worked, use it.
        # This was all a bit slow, until we cached the font size.
        cache_wrapped = {}
        cache_font = {}
        successful_sizes = []
        unsuccessful_sizes = []
        fontsize = base_fontsize
        while fontsize not in successful_sizes:
            if fontsize in unsuccessful_sizes:
                fontsize -= 1
                continue
            # logger.debug("Trying fontsize: {}".format(fontsize))
            font = get_font(ttf, fontsize)
            cache_font[fontsize] = font
            wrapped_text = word_wrap_2(text, boxwidth, font)
            textwidth, textheight = draw.textsize(wrapped_text, font)
            if textwidth > boxwidth or textheight > boxheight:
                unsuccessful_sizes.append(fontsize)
                fontsize -= 1
            else:
                successful_sizes.append(fontsize)
                cache_font[fontsize] = font
                cache_wrapped[fontsize] = wrapped_text
                fontsize += font_trial_step_size  # can go up in bigger steps
        log.debug("Wrapped final font size: {}".format(fontsize))
        font = cache_font[fontsize]
        text = cache_wrapped[fontsize]
    else:
        # The text itself is not altered.
        # Start with an arbitrary base_fontsize.
        # Calculate the size of the text in that font.
        # Rescale the font size proportionally to a font that'll fit.
        font = get_font(ttf, base_fontsize)
        basetextwidth, basetextheight = draw.textsize(text, font)
        if basetextwidth / boxwidth > basetextheight / boxheight:
            # Text is wider (as a proportion of the box) than tall.
            fontsize = int(base_fontsize * boxwidth / basetextwidth)
        else:
            # Text is taller (as a proportion of the box) than wide.
            fontsize = int(base_fontsize * boxheight / basetextheight)
        font = get_font(ttf, fontsize)
    textwidth, textheight = draw.textsize(text, font)
    log.debug(
        "Final fontsize {} (text width {}, text height {})".format(
            fontsize, textwidth, textheight
        )
    )
    if showrect:
        draw.rectangle(
            ((boxleft, boxtop), (boxleft + boxwidth, boxtop + boxheight)),
            outline=RECT_OUTLINE,
            fill=RECT_FILL,
        )
    x = justify_to_box(boxleft, boxwidth, textwidth, hjust)
    y = justify_to_box(boxtop, boxheight, textheight, vjust)
    draw.multiline_text(
        (x, y), text, rgb, font=font, align=get_align_from_hjust(hjust)
    )


# =============================================================================
# Config classes
# =============================================================================


class InputFormat(Enum):
    """
    Input format mode.
    """

    blank = "Create a blank mapping (for pen-and-paper editing)"
    debug = "Fill all boxes with text"
    demo = "Demonstrate by printing switch names"
    ed = "Elite:Dangerous binding file (.binds)"
    json = "JSON (.json; same format produced by --showmapping)"


@dataclass
class Config:
    # Input files
    format: InputFormat
    input: str

    # Elite:Dangerous options
    ed_tmw_stick: str
    ed_tmw_throttle: str
    ed_mfg_crosswind: str
    ed_horizons: bool

    # Cosmetic options
    title: Optional[str]
    subtitle: Optional[str]
    extra_text: Optional[str]
    rgbtitle: Tuple[int, int, int]
    rgbanalogue: Tuple[int, int, int]
    rgbmomentary: Tuple[int, int, int]
    rgbsticky: Tuple[int, int, int]
    ttf: str
    wrap: bool
    wrap_linesep: str

    # Debug options
    showmapping: bool
    showrects: bool
    verbose: bool

    def __post_init__(self) -> None:
        allowed_no_input = [
            InputFormat.blank,
            InputFormat.debug,
            InputFormat.demo,
        ]
        assert self.input is not None or self.format in allowed_no_input, (
            f"Must specify input unless using modes "
            f"{[x.name for x in allowed_no_input]}; "
            f"use --help for help"
        )


# =============================================================================
# Core processing functions
# =============================================================================


def make_extra_rhs_labels(config: Config) -> List[Dict[str, Any]]:
    """
    Creates extra labels for the right-hand (joystick) figure.
    """
    labels = []  # type: List[Dict[str, Any]]
    title_x_left = 50
    title_y_start = 50
    if config.title:
        labels.append(
            dict(
                text=config.title,
                x=title_x_left,
                y=title_y_start,
                fontsize=40,
                rgb=config.rgbtitle,
                hjust=0,
                vjust=0,
            )
        )
    if config.subtitle:
        labels.append(
            dict(
                text=config.subtitle,
                x=title_x_left,
                y=title_y_start + 50,
                fontsize=30,
                rgb=config.rgbtitle,
                hjust=0,
                vjust=0,
            )
        )
    if config.extra_text:
        labels.append(
            dict(
                text=config.extra_text,
                x=975,
                y=1000,
                fontsize=30,
                rgb=config.rgbtitle,
                hjust=0,
                vjust=0,
            )
        )
    return labels


def complete_blanks(masterdict: Dict[str, Dict[str, Any]]):
    """
    Populates unused options.
    """
    name_mapdict_tuples = (
        (TMW_STICK_NAME, TMW_STICK_MAP),
        (TMW_THROTTLE_NAME, TMW_THROTTLE_MAP),
        (MFG_CROSSWIND_NAME, MFG_CROSSWIND_MAP),
    )
    for name, mapdict in name_mapdict_tuples:
        devicedict = masterdict.setdefault(name, {})
        for k in mapdict.keys():
            devicedict.setdefault(k, [])


def get_mapping(config: Config) -> Dict[str, Dict[str, Any]]:
    """
    Returns a dictionary with sub-dictionaries for the stick, throttle, and
    pedals.
    """
    masterdict = {
        TMW_STICK_NAME: {},
        TMW_THROTTLE_NAME: {},
        MFG_CROSSWIND_NAME: {},
    }
    if config.format == InputFormat.blank:
        log.info("Using blank mapping")
    elif config.format == InputFormat.debug:
        log.info("Using layout debug mapping")
        v = [
            "1 2 3 4 5 6 7 8 9 0",
            "A B C D E F G H I J",
            "a b c d e f g h i j",
            # "N M O P Q R S T U V",
            # "n m o p q r s t u v",
        ]
        masterdict = {
            TMW_STICK_NAME: dict([(k, [k] + v) for k in TMW_STICK_MAP.keys()]),
            TMW_THROTTLE_NAME: dict(
                [(k, [k] + v) for k in TMW_THROTTLE_MAP.keys()]
            ),
            MFG_CROSSWIND_NAME: dict(
                [(k, [k] + v) for k in MFG_CROSSWIND_MAP.keys()]
            ),
        }
    elif config.format == InputFormat.demo:
        log.info("Using demo mapping")
        masterdict = {
            TMW_STICK_NAME: dict([(k, [k]) for k in TMW_STICK_MAP.keys()]),
            TMW_THROTTLE_NAME: dict(
                [(k, [k]) for k in TMW_THROTTLE_MAP.keys()]
            ),
            MFG_CROSSWIND_NAME: dict(
                [(k, [k]) for k in MFG_CROSSWIND_MAP.keys()]
            ),
        }
    elif config.format == InputFormat.ed:
        log.info("Using Elite Dangerous binding file {}".format(config.input))
        tree = ElementTree.parse(config.input)
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
        log.debug("XML nodes: {}".format(nodes))
        for node in nodes:
            for childbit in ["Primary", "Secondary", "Binding"]:
                child = node.find("./" + childbit)
                if child is not None and (
                    config.ed_horizons or node.tag not in ED_HORIZONS
                ):
                    process_ed_xml_node(node.tag, child, masterdict, config)
        complete_blanks(masterdict)
    elif config.format == InputFormat.json:
        log.info("Using JSON input file {}".format(config.input))
        json_data = open(config.input).read()
        masterdict = json.loads(json_data)
        complete_blanks(masterdict)
    else:
        assert False, "Bad input format: {}".format(config.format)
    return masterdict


def process_ed_xml_node(
    parenttag: ElementTree.Element,
    node: ElementTree.Element,
    masterdict: Dict[str, Dict[str, Any]],
    config: Config,
) -> None:
    """
    Modifies ``masterdict`` for Elite:Dangerous mappings.
    """
    device = node.attrib["Device"]
    key = node.attrib["Key"]
    log.debug(
        "Processing node: {}, device={}, key={}".format(parenttag, device, key)
    )
    if device == config.ed_tmw_stick:
        refmap = TMW_STICK_MAP
        refdict = masterdict[TMW_STICK_NAME]
    elif device == config.ed_tmw_throttle:
        refmap = TMW_THROTTLE_MAP
        refdict = masterdict[TMW_THROTTLE_NAME]
    elif device == config.ed_mfg_crosswind:
        refmap = MFG_CROSSWIND_MAP
        refdict = masterdict[MFG_CROSSWIND_NAME]
    else:
        return
    for ourkey, ourdict in refmap.items():
        if ourdict.get("ed") == key:
            log.debug("Found: ourkey={}".format(ourkey))
            if ourkey not in refdict:
                refdict[ourkey] = []
            nicelabel = ED_LABEL_MAP.get(parenttag, parenttag)
            refdict[ourkey].append(nicelabel)


def make_picture(
    descmap: Dict[str, str],
    placemap: Dict[str, Dict[str, int]],
    template: str,
    outfile: str,
    config: Config,
    extralabels: List[Dict[str, Any]] = None,
) -> None:
    """
    Args:
        descmap:
            dict mapping keyname -> description
        placemap:
            dict mapping keyname -> dict(l=left, r=right, t=top, b=bottom)
        template:
            template filename
        outfile:
            output filename
        config:
            top-level command arguments
        extralabels:
            list of extra label dictionaries
    """
    extralabels = extralabels or []
    log.info("Opening template: {}".format(template))
    img = Image.open(template)
    log.debug("Image size: {}".format(img.size))
    log.debug("descmap: {}".format(descmap))
    for key, desclist in descmap.items():
        if key in placemap:
            info = placemap[key]
            boxleft = info["l"]
            boxtop = info["t"]
            boxwidth = info["w"]
            boxheight = info["h"]
            type_ = info.get("type")
            if type_ == ANALOGUE:
                rgb = config.rgbanalogue
            elif type_ == STICKY:
                rgb = config.rgbsticky
            else:
                rgb = config.rgbmomentary
            boxcoords = (boxleft, boxtop, boxwidth, boxheight)
            if config.wrap:
                desc = config.wrap_linesep.join(desclist)
            else:
                desc = "\n".join(desclist)
            add_boxed_text(
                img,
                desc,
                boxcoords,
                config.ttf,
                rgb,
                showrect=config.showrects,
                hjust=info.get("hjust", 0.5),
                vjust=info.get("vjust", 0.5),
                wrap=config.wrap,
            )
    for el in extralabels:
        add_label(
            img,
            el["text"],
            el["x"],
            el["y"],
            config.ttf,
            el["fontsize"],
            el["rgb"],
            hjust=el.get("hjust", 0),
            vjust=el.get("vjust", 0),
        )
    log.info("Saving to: {}".format(outfile))
    img.save(outfile)


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    # Fetch command-line options.
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        description=r"""
(1) Generate Thrustmaster Warthog (joystick, throttle) binding pictures. Also 
    adds MFG Crosswind rudder pedal labels.

(2) For a simple example with no definitions, run
        {progname} --format demo [--showmapping]
    ... this creates pictures labelled with the switch names. 

(3) As input, it can take a JSON mapping:
        {progname} --format json --input MYFILE.json
    or an Elite:Dangerous bind file:
        {progname} --format ed --INPUT Custom.2.0.binds
    For Elite, the best thing to do is to create the bindings within Elite
    itself, then aim this script at the custom binding file.

(4) To find your Elite:Dangerous custom binding file, use: 
        dir custom*bind*.* /s /p
    Usually it is in
        %USERPROFILE%\AppData\local\Frontier Developments\Elite Dangerous\Options\Bindings

        """.format(  # noqa: E501
            progname=os.path.basename(sys.argv[0])
        ).strip(),
        formatter_class=RawDescriptionArgumentDefaultsHelpFormatter
        # formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    input_group = parser.add_argument_group("Input options")
    format_k, format_desc = keys_descriptions_from_enum(InputFormat)
    input_group.add_argument(
        "--format",
        type=str,
        choices=format_k,
        default=InputFormat.json.name,
        help=f"Input format. Possible options: ~~~ {format_desc} ~~~",
    )
    input_group.add_argument(
        "--input", default=None, help="Input file (unless 'demo' mode is used)"
    )

    output_group = parser.add_argument_group("Output files")
    output_group.add_argument(
        "--joyout",
        default=DEFAULT_JOYSTICK_OUTPUT,
        help="Joystick output file",
    )
    output_group.add_argument(
        "--throtout",
        default=DEFAULT_THROTTLE_OUTPUT,
        help="Throttle output file",
    )
    output_group.add_argument(
        "--compout",
        default=DEFAULT_COMPOSITE_OUTPUT,
        help="Composite output file",
    )

    template_group = parser.add_argument_group("Template image files")
    template_group.add_argument(
        "--joytemplate",
        default=DEFAULT_JOYSTICK_TEMPLATE,
        help="Joystick template",
    )
    template_group.add_argument(
        "--throttemplate",
        default=DEFAULT_THROTTLE_TEMPLATE,
        help="Throttle template",
    )

    ed_group = parser.add_argument_group("Elite:Dangerous options")
    ed_group.add_argument(
        "--ed_tmw_stick",
        default=DEFAULT_ED_STICK,
        help="Elite Dangerous device name for Thrustmaster Warthog joystick",
    )
    ed_group.add_argument(
        "--ed_tmw_throttle",
        default=DEFAULT_ED_THROTTLE,
        help="Elite Dangerous device name for Thrustmaster Warthog throttle/"
        "control panel",
    )
    ed_group.add_argument(
        "--ed_mfg_crosswind",
        default=DEFAULT_ED_MFG_CROSSWIND_NAME,
        help="Elite Dangerous device name for MFG Crosswind rudder pedals",
    )
    ed_group.add_argument(
        "--ed_horizons",
        action="store_true",
        help="Include bindings for Elite Dangerous: Horizons (lander buggy)",
    )

    cosmetic_group = parser.add_argument_group("Cosmetic options")
    cosmetic_group.add_argument("--title", type=str, help="Title")
    cosmetic_group.add_argument("--subtitle", type=str, help="Subtitle")
    cosmetic_group.add_argument(
        "--extra_text", type=str, help="Additional text"
    )
    cosmetic_group.add_argument(
        "--rgbtitle",
        type=rgb_tuple_from_csv,
        default=DEFAULT_RGB_TITLE,
        help="RGB colours for title/subtitle/extra text",
    )
    cosmetic_group.add_argument(
        "--rgbanalogue",
        type=rgb_tuple_from_csv,
        default=DEFAULT_RGB_ANALOGUE,
        help="RGB colours for analogue devices",
    )
    cosmetic_group.add_argument(
        "--rgbmomentary",
        type=rgb_tuple_from_csv,
        default=DEFAULT_RGB_MOMENTARY,
        help="RGB colours for momentary switches (switches that deactivate "
        "when released)",
    )
    cosmetic_group.add_argument(
        "--rgbsticky",
        type=rgb_tuple_from_csv,
        default=DEFAULT_RGB_STICKY,
        help="RGB colours for sticky switches (switches that keep their "
        "position when released)",
    )
    cosmetic_group.add_argument(
        "--ttf", default=DEFAULT_TRUETYPE_FILE, help="TrueType font file"
    )
    cosmetic_group.add_argument(
        "--wrap", action="store_true", help="Wrap text lines"
    )
    cosmetic_group.add_argument(
        "--wrap_linesep",
        type=str,
        default=" ● ",
        help="For wrapping, use this to separate multiple label lines",
    )

    debug_group = parser.add_argument_group("Debug options")
    debug_group.add_argument(
        "--showmapping", action="store_true", help="Print mapping to stdout"
    )
    debug_group.add_argument(
        "--showrects",
        action="store_true",
        help="Debugging option: show text rectangles",
    )
    debug_group.add_argument("--verbose", action="store_true", help="Verbose")

    args = parser.parse_args()
    config = Config(
        format=InputFormat[args.format],
        input=args.input,
        ed_tmw_stick=args.ed_tmw_stick,
        ed_tmw_throttle=args.ed_tmw_throttle,
        ed_mfg_crosswind=args.ed_mfg_crosswind,
        ed_horizons=args.ed_horizons,
        title=args.title,
        subtitle=args.subtitle,
        extra_text=args.extra_text,
        rgbtitle=args.rgbtitle,
        rgbanalogue=args.rgbanalogue,
        rgbmomentary=args.rgbmomentary,
        rgbsticky=args.rgbsticky,
        ttf=args.ttf,
        wrap=args.wrap,
        wrap_linesep=args.wrap_linesep,
        showmapping=args.showmapping,
        showrects=args.showrects,
        verbose=args.verbose,
    )
    logging.basicConfig(
        level=logging.DEBUG if config.verbose else logging.INFO
    )

    log.info("Thrustmaster Warthog binding diagram generator")
    log.info("By Rudolf Cardinal (rudolf@pobox.com), 2016-02-07")
    log.info(
        "Templates courtesy of rayz007, "
        "https://forums.eagle.ru/showthread.php?t=102016"
    )
    log.debug("args: {}".format(args))

    mapping = get_mapping(config)
    if args.showmapping:
        print(
            json.dumps(
                mapping, sort_keys=True, indent=4, separators=(",", ": ")
            )
        )
    make_picture(
        descmap=merge_dicts(
            mapping[TMW_STICK_NAME], mapping[MFG_CROSSWIND_NAME]
        ),
        placemap=merge_dicts(TMW_STICK_MAP, MFG_CROSSWIND_MAP),
        template=args.joytemplate,
        outfile=args.joyout,
        config=config,
        extralabels=(
            CROSSWIND_EXTRA_LABELS
            + TMW_STICK_EXTRA_LABELS
            + make_extra_rhs_labels(config)
        ),
    )
    make_picture(
        descmap=mapping[TMW_THROTTLE_NAME],
        placemap=TMW_THROTTLE_MAP,
        template=args.throttemplate,
        outfile=args.throtout,
        config=config,
        extralabels=TMW_THROTTLE_EXTRA_LABELS,
    )
    composite_side_by_side(args.compout, [args.throtout, args.joyout])


if __name__ == "__main__":
    main()
