"""
Program to determine the width and height of the monitor 
in pixels, as reported to PsychoPy.

See 

`python determine_fullscreen_pixels.py --help`

for more options.
"""

import argparse
from time import sleep
from psychopy import core, visual, gui, event


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take cli")
    parser.add_argument(
        "--screen", type=int, default=0, help="Screen number to use", required=False
    )
    parser.add_argument(
        "--no_gui",
        action="store_true",
        help="The PsychoPy GUI can break command line interface; add this flag to turn it off",
        required=False,
    )
    args = parser.parse_args()
    exp_info_dict = {"screen": args.screen}
    use_gui = not args.no_gui
    if use_gui:
        dlg = gui.DlgFromDict(
            exp_info_dict,
            title="Determine fullscreen pixels",
        )

    win = visual.Window(
        screen=exp_info_dict["screen"],
        units="pix",
        allowGUI=False,
        monitor="testMonitor",
        fullscr=True,
    )

    report_text = f"PsychoPy reports the width and height in pixels as {win.size}. \nPress any key to continue."
    visual.TextStim(win, text=report_text, wrapWidth=600, units="pix").draw()
    win.flip()
    event.waitKeys()
    print(report_text)
    win.close()
    core.quit()
