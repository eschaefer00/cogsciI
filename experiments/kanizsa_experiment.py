"""
Program to perform a "fat-thin"  yes-no discrimination task (after Ringach and Shapley).

The experiment allows running from PsychoPy standalone or from the command line.

See 

`python kanizsa_experiment.py --help`

for command line options.
"""

import numpy as np
import yaml
from psychopy import prefs

# to avoid bug on windows (https://www.psychopy.org/troubleshooting.html#errors-with-getting-setting-the-gamma-ramp)
prefs.general["gammaErrorPolicy"] = "warn"

from helper_functions import (
    FixationSpot,
    KanizsaSquare,
    convert_ms_to_frames,
    define_input_dict,
    draw_instruction,
    get_top_directory,
    save_screenshot,
)
from psychopy import core, data, event, gui, visual

TOP_DIRECTORY_PATH = get_top_directory()
if not (TOP_DIRECTORY_PATH / "data").exists():
    (TOP_DIRECTORY_PATH / "data").mkdir()


def run(exp_info_dict):
    experiment_clock = core.Clock()

    if exp_info_dict["debug"]:
        fullscreen = False
        hide_mouse = False
    else:
        fullscreen = True
        hide_mouse = True

    spatial_params = yaml.load(
        open(TOP_DIRECTORY_PATH / "experiments" / "kanizsa_params_spatial.yml"),
        yaml.Loader,
    )
    temporal_params = yaml.load(
        open(TOP_DIRECTORY_PATH / "experiments" / "kanizsa_params_temporal.yml"),
        yaml.Loader,
    )

    out_file = (
        TOP_DIRECTORY_PATH
        / "data"
        / f"experiment_1_{exp_info_dict['participant']}_{exp_info_dict['date_str']}.csv"
    )

    if exp_info_dict["practice"]:
        temporal_params["stimulus_ms"] = 1000
        temporal_params["feedback_ms"] = 500
        participant = f"{exp_info_dict['participant']}_practice"
        instruction_addition = (
            "\nThis PRACTICE MODE will show you slower trials than the real experiment."
        )
    else:
        participant = exp_info_dict["participant"]
        instruction_addition = ""

    """
    Open the psychopy drawing window
    """
    win = visual.Window(
        (1024, 768),
        screen=exp_info_dict["screen"],
        units="deg",
        allowGUI=False,
        monitor="wahrnehmen_monitor",  # monitor defined in "create_monitor_profile.py".
        fullscr=fullscreen,
    )

    if hide_mouse:
        win.setMouseVisible(False)

    # compute durations in frames, in the given window:
    timing_n_frames = {}
    for phase in temporal_params:
        rounded_n_frames, actual_duration_ms = convert_ms_to_frames(
            temporal_params[phase], win.monitorFramePeriod
        )
        print(
            f"intend time: {temporal_params[phase]} ms; actual time: {actual_duration_ms} ms"
        )
        timing_n_frames[phase.replace("_ms", "")] = rounded_n_frames
    print(timing_n_frames)

    # initiate the fixation spot in the given window:
    fixation = FixationSpot(win=win)

    # initialise kanizsa experiment:
    this_kanisza = KanizsaSquare(
        win=win, spatial_params=spatial_params, condition=exp_info_dict["condition"]
    )

    # (not important) if requested, take a screenshot prior to the time critical loop
    if exp_info_dict["screenshot"]:
        if not (TOP_DIRECTORY_PATH / "experiments" / "screenshots").exists():
            (TOP_DIRECTORY_PATH / "experiments" / "screenshots").mkdir()

        for target, signed_angle in zip(
            ["thin", "fat"], [exp_info_dict["angle"], -exp_info_dict["angle"]]
        ):
            scr_filename = (
                TOP_DIRECTORY_PATH
                / "experiments"
                / "screenshots"
                / f"kanizsa_experiment_{exp_info_dict['condition']}_{target}_{signed_angle}.png"
            )
            this_kanisza.set_ori(signed_angle)
            save_screenshot(
                fixation=fixation,
                kanisza=this_kanisza,
                screenshot_filename=scr_filename,
            )
            visual.Rect(win, fillColor=win.color, size=(1e5, 1e5)).draw()
            win.flip()  # draw a blank screen and flip to solve psychopy bug of saving wrong stimuli

    # set up trial handler to yield params.
    # See https://psychopy.org/api/data.html#psychopy.data.TrialHandler
    # See https://github.com/psychopy/psychopy/blob/release/psychopy/demos/coder/experiment%20control/TrialHandler.py
    trial_types = [{"target": "fat"}, {"target": "thin"}]

    trials = data.TrialHandler(
        trialList=trial_types,
        nReps=exp_info_dict["num_trials"],
        method="fullRandom",
        extraInfo={
            "participant": participant,
            "condition": exp_info_dict["condition"],
            **exp_info_dict,
            **spatial_params,
            **temporal_params,
        },  # the "**" unpacks the parameters dict into the top-level dict
    )

    # draw instructions:
    draw_instruction(win, exp_info_dict["condition"], instruction_addition)
    event.waitKeys()

    core.wait(1)

    """
    Here is the main trial loop
    """
    for trial in trials:
        if trial["target"] == "fat":
            # consistent with R&S, negative angles define "fat" shapes.
            signed_angle = -exp_info_dict["angle"]
            target_fat = 1.0
        else:
            signed_angle = exp_info_dict["angle"]
            target_fat = 0.0

        this_kanisza.set_ori(signed_angle)

        """
        Draw trial
        """
        trial_clock = core.Clock()

        # show stimulus
        for _ in range(timing_n_frames["stimulus"]):
            fixation.draw()
            this_kanisza.draw_pacmen()
            win.flip()

        # blank
        for _ in range(timing_n_frames["blank"]):
            fixation.draw()
            win.flip()

        # mask
        for _ in range(timing_n_frames["mask"]):
            fixation.draw()
            this_kanisza.draw_masks()
            win.flip()

        # clear screen:
        fixation.draw()
        win.flip()

        trial_time_ms = trial_clock.getTime() * 1000
        print(f"Measured trial time = {round(trial_time_ms, 1)} ms")

        """
        Collect response
        """
        response_clock = core.Clock()
        # collect response
        res = event.waitKeys(
            keyList=["j", "f", "right", "left", "escape", "q"],
            timeStamped=response_clock,
            clearEvents=True,
        )

        key, rt = res[0]  # unpack the list, assuming only one key pressed

        # classify response
        if key in ["j", "right"]:
            # "yes" or "right"
            response = 1
        elif key in ["f", "left"]:
            # "no" or "left"
            response = 0
        elif key in ["escape", "q"]:
            win.setMouseVisible(True)
            win.close()
            core.quit()

        # show feedback. Assign draw function to common variable without calling it:
        if response == target_fat:
            draw_feedback = fixation.draw_positive_feedback
        else:
            draw_feedback = fixation.draw_negative_feedback

        for _ in range(timing_n_frames["feedback"]):
            draw_feedback()
            win.flip()

        # clear screen:
        fixation.draw()
        win.flip()

        """
        Save information
        """
        # add data to trial handler:
        trials.data.add("rt_sec", rt)
        trials.data.add("response_fat", response)
        trials.data.add("target_fat", target_fat)
        trials.data.add("signed_angle", signed_angle)
        trials.data.add("measured_trial_time_ms", trial_time_ms)

        # wait for the inter-trial-interval before starting next trial:
        core.wait(temporal_params["iti_ms"] / 1000)

    # trials are finished; save data:
    df = trials.saveAsWideText(out_file)  # will append by default.
    # trials are finished; print summary:
    print("Finished!")
    print(f"\n\nData summary:\n")
    print(
        df.groupby(["signed_angle", "target"])
        .agg(
            prop_fat=("response_fat", np.mean),
            mean_rt=("rt_sec", np.mean),
            n_trials=("TrialNumber", len),
        )
        .reset_index()
    )

    print(
        f"\n\nThe experiment took {round(experiment_clock.getTime() / 60, 1)} minutes."
    )

    win.setMouseVisible(True)
    win.close()
    core.quit()


if __name__ == "__main__":
    exp_info_dict, use_gui = define_input_dict()  # can take command line input

    if use_gui:
        # assume we're running from psychopy standalone
        dlg = gui.DlgFromDict(
            exp_info_dict,
            title="Kanizsa figure experiment",
            fixed=["date_str"],
            sortKeys=False,
        )

    # before experiment starts, check input
    assert (
        exp_info_dict["angle"] > 0
    ), f"Your input angle {exp_info_dict['angle']} is invalid. Must be a positive number."
    assert exp_info_dict["condition"] in ["lo_control", "illusory"], (
        f"Your input experiment condition {exp_info_dict['condition']} is invalid. ",
        "Must be 'lo_control' or 'illusory' (without quotation marks).",
    )

    run(exp_info_dict)
