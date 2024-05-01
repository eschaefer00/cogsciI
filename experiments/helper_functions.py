"""
Helper functions
"""

import argparse
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from psychopy import data, visual


class FixationSpot(object):
    def __init__(
        self,
        win: visual.Window,
        size_deg: float = 0.15,
        pos: Tuple[float, float] = (0.0, 0.0),
    ):
        """
        Create a fixation spot instance.

        Can be used to provide feedback with colour changes.

        Args:
            win: Psychopy window to show the stimulus.
            size_deg: The diameter of the outer circle.
            pos: Position relative to the center of the window.
        """
        self.inner_radius_multiplier = 0.5
        self.inner_colour = 0.8
        self.outer_colour = -0.8

        self.win = win
        self.outer = visual.Circle(
            win=self.win,
            radius=size_deg,
            units="deg",
            pos=pos,
            fillColor=self.outer_colour,
            colorSpace="rgb",
        )
        self.inner = visual.Circle(
            win=self.win,
            radius=size_deg * self.inner_radius_multiplier,
            units="deg",
            pos=pos,
            fillColor=self.inner_colour,
            colorSpace="rgb",
        )

    def draw(self):
        self.outer.draw()
        self.inner.draw()

    def draw_positive_feedback(self):
        self.inner.fillColor = "DeepSkyBlue"
        self.outer.draw()
        self.inner.draw()

        # set inner color back after drawing:
        self.inner.fillColor = self.inner_colour

    def draw_negative_feedback(self):
        self.inner.fillColor = "DarkRed"
        self.outer.draw()
        self.inner.draw()

        # set inner color back after drawing:
        self.inner.fillColor = self.inner_colour


class KanizsaSquare(object):
    """
    Class for creating a kanizsa square.
    """

    def __init__(
        self,
        win: visual.Window,
        spatial_params: Dict,
        condition: str,
    ):
        """
        Create an instance of a KanizsaSquare class.

        Args:
            win: Psychopy window to draw on.
            alpha: Angle (deg) to rotate the inducers. < 0 creates a "fat" shape, 0 = square.
            lo_control: Is this a local orientation control condition?
            support_ratio: Ratio between pacman diameter and illusory square side length.
            eccentricity_deg: Retinal eccentricity to center of pacmen.
            contrast_proportion: Grey level of pacmen [-1, 1].
            pos: Center of Kanizsa square ( (0,0) is screen center).
        """
        self.win = win
        self.support_ratio = spatial_params["support_ratio"]
        self.eccentricity_deg = spatial_params["eccentricity_deg"]
        self.contrast_proportion = spatial_params["contrast_proportion"]
        self.center_pos = eval(spatial_params["center_pos"])

        self.square_length = self.compute_square_length()
        self.radius = self.compute_radius()

        # adapted from psychopy/demos/coder/stimuli/kanizsa.py
        # positions of the middle of the pacmen, offset by pos.
        self.pos = [
            (
                -self.square_length / 2 + self.center_pos[0],
                self.square_length / 2 + self.center_pos[1],
            ),
            (
                self.square_length / 2 + self.center_pos[0],
                self.square_length / 2 + self.center_pos[1],
            ),
            (
                -self.square_length / 2 + self.center_pos[0],
                -self.square_length / 2 + self.center_pos[1],
            ),
            (
                self.square_length / 2 + self.center_pos[0],
                -self.square_length / 2 + self.center_pos[1],
            ),
        ]

        self.condition = condition
        if self.condition == "lo_control":
            self.set_ori = self.get_pacman_pos_control
        else:
            self.set_ori = self.get_pacman_pos_illusory

        self.pie_stim = visual.Pie(
            win=self.win,
            units="deg",
            radius=self.radius,
            fillColor=self.contrast_proportion,
            colorSpace="rgb",
            start=0.0,
            end=270.0,
        )

        self.mask_stim = visual.Circle(
            win=self.win,
            units="deg",
            radius=self.radius,
            fillColor=self.contrast_proportion,
            colorSpace="rgb",
        )

    def compute_square_length(self) -> float:
        """
        compute square length -- 2x the side of one triangle,
        assuming pacmen at 45 deg.
        """
        return (
            2.0 * self.eccentricity_deg / np.sqrt(2.0)
        )  # eccentricity_deg = sqrt(2 * half_square_length ** 2)

    def compute_radius(self) -> float:
        """
        compute pacman radius from support ratio and square length (see Ringach and Shapley, p. 3038).

        > the support ratio, denotes the ratio between the diameter of one “pacman” and the
        length of the side of the illusory Kanizsa square (the distance between the centers
        of the inducers). In these experiments mu was fixed at 0.25.
        """
        return (
            self.support_ratio * self.square_length * 0.5
        )  # support_ratio = diameter / square_length

    def draw_pacmen(self) -> None:
        for i in range(4):
            self.pie_stim.pos = self.pos[i]
            self.pie_stim.ori = self.ori[i]
            self.pie_stim.draw()

    def draw_masks(self) -> None:
        for i in range(4):
            self.mask_stim.pos = self.pos[i]
            self.mask_stim.ori = self.ori[i]
            self.mask_stim.draw()

    def get_pacman_pos_control(self, alpha) -> None:
        # local orientation control
        base_orientations = (
            180.0,
            180.0,
            180.0,
            180.0,
        )
        ori_offsets = np.array([-alpha, -alpha, -alpha, -alpha])
        self.ori = base_orientations + ori_offsets

    def get_pacman_pos_illusory(self, alpha) -> None:
        # normal illusory shape condition
        base_orientations = (
            180.0,
            270.0,
            90.0,
            0.0,
        )
        ori_offsets = np.array([-alpha, alpha, alpha, -alpha])
        self.ori = base_orientations + ori_offsets


def draw_instruction(win, exp_condition, instruction_addition):
    if exp_condition == "lo_control":
        instruction_text = (
            "Are the pacmen rotated clockwise (press 'j' or 'right') or counterclockwise? "
            "(press 'f' or 'left')?"
        ) + instruction_addition
    else:
        instruction_text = (
            "Is the square 'fat' (press 'j' or 'right') or 'thin' "
            "(press 'f' or 'left')?"
        ) + instruction_addition

    instruction_text = (
        instruction_text
        + "\nTry to keep your eyes staring at the spot in the center (don't look at the pacmen directly)."
        + "\nRespond as accurately as you can. \nPress escape to exit"
        + instruction_addition
    )

    instructions = visual.TextStim(
        win,
        text=instruction_text,
        units="deg",
        wrapWidth=18,
        height=1,
    )
    instructions.draw()
    win.flip()


def save_screenshot(fixation, kanisza, screenshot_filename="screenshot.png") -> None:
    fixation.draw()
    kanisza.draw_pacmen()
    kanisza.win.getMovieFrame(
        buffer="back"
    )  # don't need to flip since we're going from the back buffer.
    kanisza.win.saveMovieFrames(fileName=screenshot_filename)


def convert_ms_to_frames(
    duration_ms: float, frame_period_sec: float
) -> Tuple[int, float]:
    """
    Convert a nominal millisecond duration into frames, with rounding.

    Args:
        duration_ms: Nominal duration in milliseconds
        frame_period_sec: the frame period (seconds per frame)

    Returns:
        A tuple of length two, containing rounded number of frames and the actual duration in ms.

    """
    rounded_n_frames = round((duration_ms / 1000) / frame_period_sec)
    actual_duration_ms = frame_period_sec * 1000 * rounded_n_frames
    return rounded_n_frames, actual_duration_ms


def get_top_directory() -> Path:
    """
    Tries to find the path to the project's top-level directory.

    Returns: a Path object to the top directory

    """
    cwd = Path.cwd()

    def correct_subdirectories(cwd):
        return (cwd / "experiments").exists() and (cwd / "notebooks").exists()

    if correct_subdirectories(cwd):
        return cwd
    elif correct_subdirectories(cwd.parent):
        return cwd.parent
    else:
        raise ValueError(f"Could not find top directory. Current directory is {cwd}")


def parse_command_line():
    """
    Function to pass command line inputs.

    Note that we have to use "required=False" for all
    parameters so that the PsychoPy gui can be used.
    This creates a danger that people don't change the
    defaults.

    Returns:
        A namespace of argparse arguments.
    """
    parser = argparse.ArgumentParser(description="Take cli")
    parser.add_argument(
        "-p",
        "--participant",
        type=str,
        default="test",
        help="Participant ID",
        required=False,
    )
    parser.add_argument(
        "-a",
        "--angle",
        type=float,
        default=1.0,
        help="The absolute pacman angle for this block.",
        required=False,
    )
    parser.add_argument(
        "--condition",
        default="illusory",
        choices=["lo_control", "illusory"],
        help="Are the signal trials with the control condition (LO control) or experimental condition?",
        required=False,
    )
    parser.add_argument(
        "-n",
        "--num_trials",
        type=int,
        default=25,
        help="The number of trials to do for each +/- angle.",
        required=False,
    )
    parser.add_argument(
        "--screen", type=int, default=0, help="Screen number to use", required=False
    )
    parser.add_argument(
        "--debug", action="store_true", help="Set to debug mode", required=False
    )
    parser.add_argument(
        "--practice",
        action="store_true",
        help="Run in practice mode (slower and with feedback)",
        required=False,
    )
    parser.add_argument(
        "--no_gui",
        action="store_true",
        help="The PsychoPy GUI can break command line interface; add this flag to turn it off",
        required=False,
    )
    parser.add_argument(
        "--screenshot",
        action="store_true",
        help="Take a screenshot",
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
        "participant": args.participant,
        "angle": float(np.abs(args.angle)),
        "condition": args.condition,
        "num_trials": args.num_trials,
        "practice": args.practice,
        "debug": args.debug,
        "screenshot": args.screenshot,
        "screen": args.screen,
    }
    exp_info_dict["date_str"] = data.getDateStr()
    return exp_info_dict, use_gui
