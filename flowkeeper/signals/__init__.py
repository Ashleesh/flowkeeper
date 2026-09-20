"""Signal collectors feed the SignalStore.

Real collectors (keyboard, window, screen) are Windows-first and optional — they
import their platform libraries lazily so the package loads anywhere. When those
libraries or the platform are unavailable, use the SimulatedSource for demos, CI,
and development on non-Snapdragon machines.
"""
from flowkeeper.signals.categorize import categorize_process
from flowkeeper.signals.simulate import SimulatedSource

__all__ = ["categorize_process", "SimulatedSource"]
