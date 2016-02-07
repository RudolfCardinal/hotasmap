## Synopsis

Create a mapping diagram for selected HOTAS (hands on throttle and stick)
gaming devices, specifically the Thrustmaster Warthog with MFG Crosswind
rudder pedals. Takes plain JSON input (for which it can generate a template),
or Elite:Dangerous key mapping files.

## Usage

    usage: hotas_map.py [-h] --format {json,ed,demo} [--input INPUT]
                        [--joyout JOYOUT] [--throtout THROTOUT]
                        [--compout COMPOUT] [--joytemplate JOYTEMPLATE]
                        [--throttemplate THROTTEMPLATE]
                        [--ed_tmw_stick ED_TMW_STICK]
                        [--ed_tmw_throttle ED_TMW_THROTTLE]
                        [--ed_mfg_crosswind ED_MFG_CROSSWIND] [--ed_horizons]
                        [--rgbanalogue RGBANALOGUE] [--rgbmomentary RGBMOMENTARY]
                        [--rgbsticky RGBSTICKY] [--showmapping] [--showrects]
                        [--ttf TTF] [--verbose]

    Generate Thrustmaster Warthog binding pictures. For a simple example, run with
    the arguments '--format demo' only.

    optional arguments:
      -h, --help            show this help message and exit
      --format {json,ed,demo}
                            Input format. Possible values: 'json' (same format as
                            produced by --showmapping); 'ed' (Elite Dangerous
                            .binds file); 'demo' (simple demonstration)
      --input INPUT         Input file (unless 'demo' mode is used)
      --joyout JOYOUT       Joystick output file (default:
                            output/output_joystick.png)
      --throtout THROTOUT   Throttle output file (default:
                            output/output_throttle.png)
      --compout COMPOUT     Composite output file (default:
                            output/output_composite.png)
      --joytemplate JOYTEMPLATE
                            Joystick template (default:
                            templates/TEMPLATE_tmw_joystick.png)
      --throttemplate THROTTEMPLATE
                            Throttle template (default:
                            templates/TEMPLATE_tmw_throttle.png)
      --ed_tmw_stick ED_TMW_STICK
                            Elite Dangerous device name for Thrustmaster Warthog
                            joystick (default: ThrustMasterWarthogJoystick)
      --ed_tmw_throttle ED_TMW_THROTTLE
                            Elite Dangerous device name for Thrustmaster Warthog
                            throttle/control panel (default:
                            ThrustMasterWarthogThrottle)
      --ed_mfg_crosswind ED_MFG_CROSSWIND
                            Elite Dangerous device name for MFG Crosswind rudder
                            pedals (default: 16D00A38)
      --ed_horizons         Include bindings for Elite Dangerous: Horizons (lander
                            buggy)
      --rgbanalogue RGBANALOGUE
                            RGB colours for analogue devices (default: 255,0,255)
      --rgbmomentary RGBMOMENTARY
                            RGB colours for momentary switches (switches that
                            deactivate when released; default: 255,0,0)
      --rgbsticky RGBSTICKY
                            RGB colours for sticky switches (switches that keep
                            their position when released; default: 0,0,255)
      --showmapping         Print mapping to stdout
      --showrects           Debugging option: show text rectangles
      --ttf TTF             TrueType font file (default: Arial_Bold.ttf)
      --verbose             Verbose
