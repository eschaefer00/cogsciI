"""
Create a PsychoPy monitor profile and validate it visually.

Can be run from PsychoPy standalone or from command line.

python create_monitor_profile.py --help

for usage and further description. 
"""

import argparse
from time import sleep
from typing import Dict, Tuple

import numpy as np
from psychopy import prefs

# to avoid bug on windows (https://www.psychopy.org/troubleshooting.html#errors-with-getting-setting-the-gamma-ramp)
prefs.general["gammaErrorPolicy"] = "warn"
from psychopy import core, event, gui, logging, monitors, visual


def parse_command_line():
    """
    Function to pass command line inputs

    Returns:
        A namespace of argparse arguments.
    """
    parser = argparse.ArgumentParser(description="Take cli")
    parser.add_argument(
        "--width_cm",
        type=float,
        default=0.0,
        help="The width of your monitor in cm",
        required=False,
    )
    parser.add_argument(
        "--distance_cm",
        type=float,
        default=0.0,
        help="Your viewing distance in cm",
        required=False,
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.0,
        help="Gamma value computed in homework_1",
        required=False,
    )
    parser.add_argument(
        "--width_px",
        type=int,
        default=0,
        help="Width of your monitor in px",
        required=False,
    )
    parser.add_argument(
        "--height_px",
        type=int,
        default=0,
        help="Height of your monitor in px",
        required=False,
    )
    parser.add_argument(
        "--screen", type=int, default=0, help="Screen number to use", required=False
    )
    parser.add_argument(
        "--debug", action="store_true", help="Set to debug mode", required=False
    )
    parser.add_argument(
        "--no_gui",
        action="store_true",
        help="The PsychoPy GUI can break command line interface; add this flag to turn it off",
        required=False,
    )
    args = parser.parse_args()
    return args


def define_input_dict() -> Tuple[Dict, bool]:
    """
    Define an input dictionary with parameters.

    Default params will be set in argparse
    defaults, and can be changed either through
    the cli or through PsychoPy's gui.

    Returns:
        Tuple[Dict, bool]: A tuple containing a
            parameters dictionary and a boolean
            determining whether to use PsychoPy's
            gui or not.
    """
    args = parse_command_line()
    use_gui = not args.no_gui
    exp_info_dict = {
        "width_cm": args.width_cm,
        "distance_cm": args.distance_cm,
        "gamma": args.gamma,
        "width_px": args.width_px,
        "height_px": args.height_px,
        "screen": args.screen,
        "debug": args.debug,
    }
    return exp_info_dict, use_gui


def run(exp_info_dict):
    if exp_info_dict["debug"]:
        logging.console.setLevel(logging.DEBUG)
        fullscreen = False
        hide_mouse = False
    else:
        logging.console.setLevel(logging.ERROR)
        fullscreen = True
        hide_mouse = True

    monitor = monitors.Monitor(
        "wahrnehmen_monitor",
        width=exp_info_dict["width_cm"],
        distance=exp_info_dict["distance_cm"],
        gamma=[exp_info_dict["gamma"], exp_info_dict["gamma"], exp_info_dict["gamma"]],
        notes="Monitor set up for the CogSci course Wahrnehmen.",
    )
    monitor.setSizePix((exp_info_dict["width_px"], exp_info_dict["height_px"]))

    # open a window:
    win = visual.Window(
        size=(1024, 768),
        monitor=monitor,
        units="deg",
        fullscr=fullscreen,
        screen=exp_info_dict["screen"],
    )
    if hide_mouse:
        win.setMouseVisible(False)

    text_stim = visual.TextStim(
        win,
        text="Checking framerate. Press any key to continue.",
        units="deg",
        wrapWidth=20,
        height=0.5,
    )
    text_stim.draw()
    win.flip()
    event.waitKeys()

    fps = win.getMsPerFrame(
        showVisual=True
    )  # returns a three element tuple; third is median.
    logging.log(
        level=logging.DEBUG, msg=f"Measured fps values (mean, sd, median) are {fps}"
    )

    fps_rounded = round(fps[2], 2)

    text_stim.text = f"Calculated ms per frame as {fps_rounded} (approx. {round(1000 / fps_rounded)} Hz refresh rate)."
    text_stim.draw()
    win.flip()
    sleep(2)

    text_stim.text = f"Now displaying gamma pattern. Press any key to continue."
    text_stim.draw()
    win.flip()
    event.waitKeys()

    # display grating vs grey. If gamma is working correctly, should have approx same luminance:
    win_x, win_y = win.size
    stim_size_x = win_x / 2
    stim_size_y = win_y

    # create a grey square to fill one side of the screen.
    grey_rect = visual.Rect(
        win,
        units="pix",
        size=(stim_size_x, stim_size_y),
        fillColor=0.0,
        pos=(stim_size_x / 2, 0),
        colorSpace="rgb",  # color defined [-1, 1]
    )

    # create a numpy array of black-white lines, alternating each pixel:
    stim = np.ones((int(stim_size_y), int(stim_size_x))) * 0.0
    stim[::2, :] = 1.0
    stim = np.repeat(stim[:, :, np.newaxis], repeats=3, axis=2)

    grating = visual.ImageStim(
        win,
        image=stim,
        units="pix",
        pos=(-stim_size_x / 2, 0),
        size=(stim_size_x, stim_size_y),
        colorSpace="rgb1",
    )

    text_stim.text = "left and right should have approx same luminance when standing back. Press any key to continue..."

    grating.draw()
    grey_rect.draw()
    text_stim.draw()
    win.flip()
    event.waitKeys()

    # check size by displaying a 2 deg diameter circle:
    text_stim.text = (
        "Now displaying a 2 deg diameter circle. "
        "\nCheck with the 'rule of thumb': this circle should be approximately the same size as your thumb with your arm held straight."
        "\nIf the circle is about twice the size of your thumb, then you likely have a Retina or otherwise HD display."
        "\nIn this case, try re-running this program but halve the pixel width and height of your monitor."
        "\nPress a key to continue."
    )
    text_stim.draw()
    win.flip()
    event.waitKeys()

    circle_stim = visual.Circle(win, radius=1.0, units="deg", fillColor=-1.0)
    circle_stim.draw()
    win.flip()
    event.waitKeys()

    # save monitor out:
    monitor.save()

    win.setMouseVisible(True)
    win.close()
    core.quit()


if __name__ == "__main__":
    exp_info_dict, use_gui = define_input_dict()  # can take command line input

    if use_gui:
        logging.log(level=logging.INFO, msg="Using psychopy gui")
        # assume we're running from psychopy standalone
        dlg = gui.DlgFromDict(exp_info_dict, title="Create and test monitor profile")
    else:
        # user turned off gui (running from cli)
        logging.log(level=logging.INFO, msg="Not using psychopy gui")

    run(exp_info_dict)
