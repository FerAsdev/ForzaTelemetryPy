"""
GUI Track – colored trace by acceleration/brake + zoom buttons
Author: ChatGPT (auto‑generated)

Features
--------
* Always rotates the racing line 90° CCW for optimal use of horizontal space.
* Auto‑detects Throttle/Brake columns and normalizes ranges (0‑1, 0‑100, 0‑255).
* Zoom In / Zoom Out / Reset buttons via matplotlib.widgets.Button.
* Responsive layout: minimal margins and subplots adjusted to fill available width.

Usage
-----
from gui_track_colored import plot_track_colored
fig = plot_track_colored(lap_df, lap_number=10)
fig.show()
"""

from __future__ import annotations
import math
from typing import Sequence, Union, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import TwoSlopeNorm
from matplotlib.widgets import Button

# -----------------------------------------------------------------------------
# Column detection and normalization
# -----------------------------------------------------------------------------
_THROTTLE_CANDIDATES: Tuple[str, ...] = (
    "Throttle", "ThrottleInput", "Accel", "Accelerator", "Gas"
)
_BRAKE_CANDIDATES: Tuple[str, ...] = (
    "Brake", "BrakeInput", "Brakes", "BrakePedal"
)

def _find_column(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _normalize(series: Union[pd.Series, np.ndarray, Sequence[float]]) -> np.ndarray:
    arr = np.asarray(series, dtype=float)
    arr = np.nan_to_num(arr, nan=0.0)
    mx = arr.max(initial=0.0)
    if mx <= 1.0:
        return arr
    if mx <= 100.0:
        return arr / 100.0
    if mx <= 255.0:
        return arr / 255.0
    return arr / mx

# -----------------------------------------------------------------------------
# Rotation
# -----------------------------------------------------------------------------
def _rotate90(x: np.ndarray, z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    return z, -x  # CCW 90°

# -----------------------------------------------------------------------------
# Zoom controls
# -----------------------------------------------------------------------------
def _attach_zoom_buttons(fig: plt.Figure, ax: plt.Axes, base_scale: float = 1.2) -> None:
    btn_w, btn_h, pad = 0.05, 0.04, 0.005
    right, top = 0.92, 0.95
    ax_in = fig.add_axes([right, top - btn_h, btn_w, btn_h])
    ax_out = fig.add_axes([right, top - 2*(btn_h+pad), btn_w, btn_h])
    ax_rst = fig.add_axes([right, top - 3*(btn_h+pad), btn_w, btn_h])
    btn_in = Button(ax_in, '+')
    btn_out = Button(ax_out, '−')
    btn_rst = Button(ax_rst, '⟳')
    orig_xlim, orig_ylim = ax.get_xlim(), ax.get_ylim()
    def _zoom(factor: float):
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        cx, cy = (x0+x1)/2, (y0+y1)/2
        w, h = (x1-x0)/factor, (y1-y0)/factor
        ax.set_xlim(cx - w/2, cx + w/2)
        ax.set_ylim(cy - h/2, cy + h/2)
        fig.canvas.draw_idle()
    btn_in.on_clicked(lambda _: _zoom(base_scale))
    btn_out.on_clicked(lambda _: _zoom(1/base_scale))
    btn_rst.on_clicked(lambda _: (ax.set_xlim(*orig_xlim), ax.set_ylim(*orig_ylim), fig.canvas.draw_idle()))

# -----------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------

def plot_track_colored(
    lap_df: pd.DataFrame,
    lap_number: int,
    throttle_col: Optional[str] = None,
    brake_col: Optional[str] = None,
    cmap: str = 'RdYlGn',
    line_width: float = 2.0,
    zoom_buttons: bool = True,
) -> plt.Figure:
    # Check positions
    if 'PositionX' not in lap_df.columns or 'PositionZ' not in lap_df.columns:
        fig, ax = plt.subplots(figsize=(6,6))
        ax.text(0.5, 0.5, "Faltan PosX/PosZ", ha='center', va='center', transform=ax.transAxes)
        return fig
    # Detect columns
    throttle_col = throttle_col or _find_column(lap_df, _THROTTLE_CANDIDATES)
    brake_col = brake_col or _find_column(lap_df, _BRAKE_CANDIDATES)
    if not throttle_col and not brake_col:
        fig, ax = plt.subplots(figsize=(6,6))
        ax.text(0.5,0.5,"No Throttle/Brake",ha='center',va='center',transform=ax.transAxes)
        return fig
    thr = _normalize(lap_df.get(throttle_col, 0.0))
    brk = _normalize(lap_df.get(brake_col, 0.0))
    load = thr - brk
    # coords & rotate
    x = lap_df['PositionX'].to_numpy(); z = lap_df['PositionZ'].to_numpy()
    x, z = _rotate90(x, z)
    # build figure
    fig, ax = plt.subplots(figsize=(9,6))
    pts = np.column_stack([x,z]).reshape(-1,1,2)
    segs = np.concatenate([pts[:-1], pts[1:]],axis=1)
    vmin, vmax = float(load.min()), float(load.max())
    if math.isclose(vmin,vmax): vmin,vmax=-1,1
    norm = TwoSlopeNorm(vmin=vmin,vcenter=0,vmax=vmax)
    lc = LineCollection(segs, cmap=cmap, norm=norm, linewidth=line_width)
    lc.set_array(load[:-1])
    ax.add_collection(lc)
    ax.autoscale(); ax.set_aspect('equal','box')
    ax.set_xlabel('Position X (m)'); ax.set_ylabel('Position Z (m)')
    ax.set_title(f'Vuelta {lap_number}: Trazada Acceler/Freno')
    cbar = fig.colorbar(lc, ax=ax, fraction=0.02, pad=0.01)
    cbar.set_label('-1 Brake  0 Neutral  +1 Throttle')
    ax.grid(True, linestyle=':', linewidth=0.5)
    # adjust margins
    fig.subplots_adjust(left=0.05, right=0.90, top=0.90, bottom=0.05)
    if zoom_buttons:
        _attach_zoom_buttons(fig, ax)
    return fig
