# Some simple test functions for experiments

import numpy as np


from helper_functions import (
    KanizsaSquare,
    convert_ms_to_frames,
)


def test_compute_square_length():
    np.testing.assert_approx_equal(KanizsaSquare.compute_square_length(4), 5.656854249)
    np.testing.assert_approx_equal(KanizsaSquare.compute_square_length(6), 8.485281374)
    np.testing.assert_approx_equal(KanizsaSquare.compute_square_length(12), 16.9705627)


def test_compute_radius():
    np.testing.assert_approx_equal(KanizsaSquare.compute_radius(0.25, 4), 0.5)
    np.testing.assert_approx_equal(KanizsaSquare.compute_radius(0.5, 4), 1.0)
    np.testing.assert_approx_equal(KanizsaSquare.compute_radius(0.25, 12), 1.5)


def test_convert_ms_to_frames():
    n_frames, actual_duration = convert_ms_to_frames(117, 1 / 60)
    assert 7 == n_frames
    np.testing.assert_approx_equal(actual_duration, 116.6666666667)
