"""
fractal_tree.py

Python module for interactive visualization of fractal trees using Matplotlib or Tkinter GUI.

Usage:
    $ python fractal_tree.py           # Matplotlib interactive sliders and live animation (default)
    $ python fractal_tree.py --mode tk  # Tkinter GUI
    $ python fractal_tree.py --depth 10 --angle 25 --factor 0.65  # custom parameters
    $ python fractal_tree.py --save output.png  # save a static snapshot and exit
"""
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class FractalTree:
    """
    Generates fractal trees with enhanced visuals and animation.
    """

    def __init__(self, depth=8, angle=30, factor=0.7, seed=0, cmap_tree='Greens'):
        self.depth = depth
        self.angle = np.deg2rad(angle)
        self.factor = factor
        self.cmap_tree = cmap_tree

    def draw_tree(self, ax, x=0, y=0, length=1, angle=None, depth=None):
        current_depth = depth if depth is not None else self.depth
        current_angle = angle if angle is not None else np.pi / 2
        if current_depth == 0:
            return
        t = current_depth / self.depth
        # get branch gradient from colormap
        cmap = plt.get_cmap(self.cmap_tree)
        color = cmap(t)
        linewidth = 0.5 + current_depth * 0.3
        x2 = x + length * np.cos(current_angle)
        y2 = y + length * np.sin(current_angle)
        ax.plot([x, x2], [y, y2], color=color, linewidth=linewidth)
        new_length = length * self.factor
        self.draw_tree(ax, x2, y2, new_length, current_angle + self.angle, current_depth - 1)
        self.draw_tree(ax, x2, y2, new_length, current_angle - self.angle, current_depth - 1)

    def draw_structures(self, ax, step=0):
        ax.clear()
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_facecolor('#f0f8ff')
        self.draw_tree(ax)
        ax.set_aspect('equal')
        ax.set_title('Fractal Tree', pad=10)


class MatplotlibApp(FractalTree):
    """
    Matplotlib application with interactive sliders and live animation.
    """

    def run(self, save_path=None):
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('#ececec')
        fig.suptitle('Fractal Tree Visualization', fontsize=16, weight='bold')
        plt.subplots_adjust(left=0.1, bottom=0.25)

        axcolor = 'lightgray'
        slider_axes = {
            'Depth': plt.axes([0.1, 0.15, 0.8, 0.03], facecolor=axcolor),
            'Angle': plt.axes([0.1, 0.10, 0.8, 0.03], facecolor=axcolor),
            'Factor': plt.axes([0.1, 0.05, 0.8, 0.03], facecolor=axcolor)
        }
        sliders = {
            'Depth': Slider(slider_axes['Depth'], 'Depth', 1, 12, valinit=self.depth, valstep=1),
            'Angle': Slider(slider_axes['Angle'], 'Angle', 0, 90, valinit=np.rad2deg(self.angle)),
            'Factor': Slider(slider_axes['Factor'], 'Factor', 0.5, 0.9, valinit=self.factor)
        }

        def update(val):
            self.depth = int(sliders['Depth'].val)
            self.angle = np.deg2rad(sliders['Angle'].val)
            self.factor = sliders['Factor'].val

        for s in sliders.values():
            s.on_changed(update)

        if save_path:
            self.draw_structures(ax, step=0)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to {save_path}")
            return

        # keep a reference to the animation and disable unbounded frame caching
        self.anim = FuncAnimation(
            fig,
            lambda i: self.draw_structures(ax, i),
            interval=100,
            cache_frame_data=False
        )
        plt.show()


class TkinterApp(FractalTree):
    """
    Tkinter GUI embedding animated Matplotlib figure with controls.
    """

    def run(self):
        root = tk.Tk()
        root.title('Fractal Tree')
        control = ttk.Frame(root, padding=10)
        control.pack(side=tk.LEFT, fill=tk.Y)
        plot = ttk.Frame(root)
        plot.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

        fig = Figure(figsize=(6, 6), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor('#ececec')

        canvas = FigureCanvasTkAgg(fig, master=plot)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        params = {
            'Depth': tk.IntVar(value=self.depth),
            'Angle': tk.DoubleVar(value=np.rad2deg(self.angle)),
            'Factor': tk.DoubleVar(value=self.factor)
        }
        ranges = {'Depth': (1, 12), 'Angle': (0, 90), 'Factor': (0.5, 0.9)}

        for i, (k, v) in enumerate(params.items()):
            ttk.Label(control, text=k).grid(row=i, column=0, sticky=tk.W)
            ttk.Scale(control, variable=v, from_=ranges[k][0], to=ranges[k][1], orient=tk.HORIZONTAL).grid(row=i,
                                                                                                           column=1,
                                                                                                           sticky=tk.EW)
            control.columnconfigure(1, weight=1)
            v.trace_add('write', lambda *a, key=k: setattr(self, key.lower(), float(params[key].get())))

        self.draw_structures(ax, step=0)
        canvas.draw()

        def animate(i):
            self.draw_structures(ax, i)
            canvas.draw_idle()

        # keep a reference to the animation and disable unbounded frame caching
        self.anim = FuncAnimation(
            fig,
            animate,
            interval=100,
            cache_frame_data=False
        )
        root.mainloop()


def main():
    parser = argparse.ArgumentParser(description='Interactive fractal tree visualization')
    parser.add_argument('--mode', choices=['plt', 'tk'], default='plt',
                        help='Choose visualization mode: plt (Matplotlib) or tk (Tkinter).')
    parser.add_argument('--depth', type=int, default=8, help='Recursion depth for fractal tree')
    parser.add_argument('--angle', type=float, default=30, help='Branch angle in degrees')
    parser.add_argument('--factor', type=float, default=0.7, help='Branch length factor')
    parser.add_argument('--seed', type=int, default=0, help='Random seed for initialization')
    parser.add_argument('--cmap-tree', default='Greens', help='Matplotlib colormap for tree')
    parser.add_argument('--save', help='Path to save a static snapshot (PNG) and exit')
    args = parser.parse_args()

    if args.mode == 'tk':
        app = TkinterApp(depth=args.depth, angle=args.angle, factor=args.factor,
                         seed=args.seed, cmap_tree=args.cmap_tree)
        app.run()
    else:
        app = MatplotlibApp(depth=args.depth, angle=args.angle, factor=args.factor,
                            seed=args.seed, cmap_tree=args.cmap_tree)
        app.run(save_path=args.save)


if __name__ == '__main__':
    main()