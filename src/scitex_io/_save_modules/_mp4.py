#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 16:57:29 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_save_mp4.py


def _mk_mp4(fig, spath_mp4):
    """Create an MP4 animation from a matplotlib figure.

    matplotlib is lazy-imported inside the function body so that
    ``import scitex.io`` (and the parent ``import scitex``) does not
    fail on venvs without matplotlib installed (todo#443, same class
    as #279 / #441 / #442). Without lazy-import, the eager top-level
    ``from matplotlib import animation`` propagated ``ModuleNotFoundError``
    up the ``_save_modules.__init__`` walk and broke any caller of
    ``scitex.io.save(dict, "out.json")`` who had no business needing
    matplotlib.
    """
    from matplotlib import animation  # lazy: see todo#443

    axes = fig.get_axes()

    def init():
        return (fig,)

    def animate(i):
        for ax in axes:
            ax.view_init(elev=10.0, azim=i)
        return (fig,)

    anim = animation.FuncAnimation(
        fig, animate, init_func=init, frames=360, interval=20, blit=True
    )

    writermp4 = animation.FFMpegWriter(fps=60, extra_args=["-vcodec", "libx264"])
    anim.save(spath_mp4, writer=writermp4)
    print("\nSaving to: {}\n".format(spath_mp4))


# EOF
