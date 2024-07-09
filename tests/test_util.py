"""
This module contains the unit tests for the `utils` module from the `lameg` package.
"""
import numpy as np

from lameg.util import check_many, spm_context, big_brain_proportional_layer_boundaries
from spm import spm_standalone


def test_spm_context():
    """
    Test the spm_context to ensure proper execution and capture stdout
    """
    # Check opening new instance with context manager
    with spm_context() as spm:
        assert spm.name == 'spm_standalone'

        ver = spm.spm(
            "Version",
            nargout=1
        )
        assert ver == 'SPM (dev)'

    # Check that instance is terminated
    terminated = False
    try:
        ver = spm.spm(
            "Version",
            nargout=1
        )
    except RuntimeError:
        terminated = True
    assert terminated

    # Check using existing instance with context manager
    spm_instance = spm_standalone.initialize()
    with spm_context(spm_instance) as spm:
        assert spm.name == 'spm_standalone'

        ver = spm.spm(
            "Version",
            nargout=1
        )
        assert ver == 'SPM (dev)'

    # Check that not terminated
    ver = spm.spm(
        "Version",
        nargout=1
    )
    assert ver == 'SPM (dev)'

    spm_instance.terminate()

    # Check that terminated
    terminated = False
    try:
        ver = spm.spm(
            "Version",
            nargout=1
        )
    except RuntimeError:
        terminated = True
    assert terminated


def test_check_many():
    """
    Test the `check_many` function to verify its response to different scenarios and parameters.

    The function is tested to:
    - Throw a ValueError when `target` contains characters not in `multiple` (when applicable).
    - Correctly return True if any or all elements in `multiple` are in `target` based on the
      `func` parameter.
    - Correctly return False if not all or none of the elements in `multiple` are in `target`,
      based on the `func` parameter.

    Tests include:
    - Single element in `multiple` that is part of `target`.
    - Multiple elements in `multiple` with partial inclusion in `target`.
    - Multiple elements in `multiple` fully included in `target`.
    - No elements from `multiple` included in `target`.

    Args:
        None

    Returns:
        None
    """

    multiple = ['x']
    target = 'xy'
    val_error = False
    try:
        check_many(multiple, target)
    except ValueError:
        val_error = True
    assert val_error

    multiple = ['x', 'y']
    target = 'x'
    assert check_many(multiple, target, func='any')

    multiple = ['x', 'y']
    target = 'z'
    assert not check_many(multiple, target, func='any')

    multiple = ['x', 'x']
    target = 'x'
    assert check_many(multiple, target, func='all')

    multiple = ['x', 'y']
    target = 'x'
    assert not check_many(multiple, target, func='all')

    multiple = ['x', 'y']
    target = 'z'
    assert not check_many(multiple, target, func='all')


def test_big_brain_proportional_layer_boundaries():
    """
    Tests the big_brain_proportional_layer_boundaries function to ensure it returns accurate and
    expected layer boundary data for both left hemisphere (lh) and right hemisphere (rh).

    This function performs the following checks:
    - Asserts that the 'lh' and 'rh' keys exist in the returned dictionary.
    - Asserts that the shape of the arrays for 'lh' and 'rh' is correct, verifying the number of
      layers (6) and the expected number of vertices (163842).
    - Checks that the first column of each hemisphere's data closely matches a predefined expected
      array of layer boundary values, with a tolerance for maximum absolute difference set to less
      than 1e-6.

    The function is called twice to verify the consistency of outputs:
    - First with the `overwrite` parameter set to False.
    - Then with the `overwrite` parameter set to True.

    Raises:
        AssertionError: If any of the assertions fail, indicating that the expected data structure
        or values are incorrect or missing.
    """

    bb_data = big_brain_proportional_layer_boundaries(overwrite=False)

    assert 'lh' in bb_data
    assert bb_data['lh'].shape[0] == 6 and bb_data['lh'].shape[1] == 163842
    expected = np.array([0.07864515, 0.13759026, 0.3424378, 0.4091583, 0.64115983, 1])
    assert np.max(np.abs(bb_data['lh'][:, 0] - expected)) < 1e-6

    assert 'rh' in bb_data
    assert bb_data['rh'].shape[0] == 6 and bb_data['rh'].shape[1] == 163842
    expected = np.array([0.07103447, 0.15451714, 0.46817848, 0.53011256, 0.7344828, 1.])
    assert np.max(np.abs(bb_data['rh'][:, 0] - expected)) < 1e-6

    bb_data = big_brain_proportional_layer_boundaries(overwrite=True)

    assert 'lh' in bb_data
    assert bb_data['lh'].shape[0] == 6 and bb_data['lh'].shape[1] == 163842
    expected = np.array([0.07864515, 0.13759026, 0.3424378, 0.4091583, 0.64115983, 1])
    assert np.max(np.abs(bb_data['lh'][:, 0] - expected)) < 1e-6

    assert 'rh' in bb_data
    assert bb_data['rh'].shape[0] == 6 and bb_data['rh'].shape[1] == 163842
    expected = np.array([0.07103447, 0.15451714, 0.46817848, 0.53011256, 0.7344828, 1.])
    assert np.max(np.abs(bb_data['rh'][:, 0] - expected)) < 1e-6