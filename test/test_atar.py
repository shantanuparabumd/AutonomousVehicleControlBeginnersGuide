"""
Test of A* Algorithm

Author: Shantanu Parab
"""

from pathlib import Path
import sys
import pytest

sys.path.append(str(Path(__file__).absolute().parent) + "/../src/components/planning/astar")
import astar


def test_simulation():
    astar.show_plot = False
    astar.main()
