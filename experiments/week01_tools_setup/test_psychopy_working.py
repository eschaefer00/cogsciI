"""
Tests to see that we can open psychopy windows and display things.
"""

from psychopy import prefs

# to avoid bug on windows (https://www.psychopy.org/troubleshooting.html#errors-with-getting-setting-the-gamma-ramp)
prefs.general["gammaErrorPolicy"] = "warn"

from psychopy import core, visual


def test_open_window():
    # Open a PsychoPy window, display test text
    win = visual.Window(
        (1024, 768),
        screen=0,
        allowGUI=False,
        fullscr=True,
    )
    text = visual.TextStim(
        win,
        text="Seems to be working!",
    )
    text.draw()
    win.flip()

    core.wait(1)

    win.flip()
    win.close()


if __name__ == "__main__":
    test_open_window()
