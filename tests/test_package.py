from importlib.metadata import version

import seamcarver
from seamcarver.calculator import SeamCalculator
from seamcarver.methods import EnergyMethod


def test_version_matches_distribution():
    assert seamcarver.__version__ == version("seamcarver")


def test_top_level_exports_are_intentional():
    assert set(seamcarver.__all__) == {
        "ResizePlan",
        "resize",
        "plan",
        "GradientEnergy",
        "LaplacianEnergy",
        "SobelEnergy",
        "__version__",
    }
    assert not hasattr(seamcarver, "SeamCalculator")
    assert not hasattr(seamcarver, "EnergyMethod")


def test_advanced_interfaces_remain_in_submodules():
    assert SeamCalculator.__module__ == "seamcarver.calculator"
    assert EnergyMethod.__module__ == "seamcarver.methods.interface"
    assert not hasattr(SeamCalculator, "mask_to_index")
