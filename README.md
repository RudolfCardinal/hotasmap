## Synopsis

Create a mapping diagram for selected HOTAS (hands on throttle and stick)
gaming devices, specifically the Thrustmaster Warthog with MFG Crosswind
rudder pedals. Takes plain JSON input (for which it can generate a template),
or Elite:Dangerous key mapping files.

## Usage
    
    usage: hotas_map.py [-h] [--format {blank,debug,demo,ed,json}] [--input INPUT]
                        [--joyout JOYOUT] [--throtout THROTOUT]
                        [--compout COMPOUT] [--joytemplate JOYTEMPLATE]
                        [--throttemplate THROTTEMPLATE]
                        [--ed_tmw_stick ED_TMW_STICK]
                        [--ed_tmw_throttle ED_TMW_THROTTLE]
                        [--ed_mfg_crosswind ED_MFG_CROSSWIND] [--ed_horizons]
                        [--title TITLE] [--subtitle SUBTITLE]
                        [--extra_text EXTRA_TEXT] [--rgbtitle RGBTITLE]
                        [--rgbanalogue RGBANALOGUE] [--rgbmomentary RGBMOMENTARY]
                        [--rgbsticky RGBSTICKY] [--ttf TTF] [--wrap]
                        [--wrap_linesep WRAP_LINESEP] [--showmapping]
                        [--showrects] [--verbose]
    
    (1) Generate Thrustmaster Warthog (joystick, throttle) binding pictures. Also 
        adds MFG Crosswind rudder pedal labels.
    
    (2) For a simple example with no definitions, run
            hotas_map.py --format demo [--showmapping]
        ... this creates pictures labelled with the switch names. 
    
    (3) As input, it can take a JSON mapping:
            hotas_map.py --format json --input MYFILE.json
        or an Elite:Dangerous bind file:
            hotas_map.py --format ed --INPUT Custom.2.0.binds
        For Elite, the best thing to do is to create the bindings within Elite
        itself, then aim this script at the custom binding file.
    
    (4) To find your Elite:Dangerous custom binding file, use: 
            dir custom*bind*.* /s /p
        Usually it is in
            %USERPROFILE%\AppData\local\Frontier Developments\Elite Dangerous\Options\Bindings
    
    optional arguments:
      -h, --help            show this help message and exit
    
    Input options:
      --format {blank,debug,demo,ed,json}
                            Input format. Possible options: ~~~ blank: Create a
                            blank mapping (for pen-and-paper editing) // debug:
                            Fill all boxes with text // demo: Demonstrate by
                            printing switch names // ed: Elite:Dangerous binding
                            file (.binds) // json: JSON (.json; same format
                            produced by --showmapping) ~~~ (default: json)
      --input INPUT         Input file (unless 'demo' mode is used) (default:
                            None)
    
    Output files:
      --joyout JOYOUT       Joystick output file (default: /home/rudolf/Documents/
                            code/hotasmap/output/output_joystick.png)
      --throtout THROTOUT   Throttle output file (default: /home/rudolf/Documents/
                            code/hotasmap/output/output_throttle.png)
      --compout COMPOUT     Composite output file (default: /home/rudolf/Documents
                            /code/hotasmap/output/output_composite.png)
    
    Template image files:
      --joytemplate JOYTEMPLATE
                            Joystick template (default: /home/rudolf/Documents/cod
                            e/hotasmap/templates/TEMPLATE_tmw_joystick.png)
      --throttemplate THROTTEMPLATE
                            Throttle template (default: /home/rudolf/Documents/cod
                            e/hotasmap/templates/TEMPLATE_tmw_throttle.png)
    
    Elite:Dangerous options:
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
                            buggy) (default: False)
    
    Cosmetic options:
      --title TITLE         Title (default: None)
      --subtitle SUBTITLE   Subtitle (default: None)
      --extra_text EXTRA_TEXT
                            Additional text (default: None)
      --rgbtitle RGBTITLE   RGB colours for title/subtitle/extra text (default:
                            0,100,0)
      --rgbanalogue RGBANALOGUE
                            RGB colours for analogue devices (default: 255,0,255)
      --rgbmomentary RGBMOMENTARY
                            RGB colours for momentary switches (switches that
                            deactivate when released) (default: 255,0,0)
      --rgbsticky RGBSTICKY
                            RGB colours for sticky switches (switches that keep
                            their position when released) (default: 0,0,255)
      --ttf TTF             TrueType font file (default: Arial_Bold.ttf)
      --wrap                Wrap text lines (default: False)
      --wrap_linesep WRAP_LINESEP
                            For wrapping, use this to separate multiple label
                            lines (default: ● )
    
    Debug options:
      --showmapping         Print mapping to stdout (default: False)
      --showrects           Debugging option: show text rectangles (default:
                            False)
      --verbose             Verbose (default: False)
