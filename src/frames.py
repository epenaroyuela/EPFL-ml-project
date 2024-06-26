"""Compedium of functions to manipulate frames, to be used with *Capture"""
import numpy as np


def select_channel(channel):
    """Selects a single channel"""

    def _inner(i, frame):
        frame = frame[:, :, channel : channel + 1]
        return frame

    return _inner


def plicate_channel(channels):
    """N-plicates the channels"""

    def _inner(i, frame):
        frame = np.concatenate((frame, frame, frame), axis=2)
        return frame

    return _inner


def cast(type):
    """Casts the type of the underlying matrix"""

    def _inner(i, frame):
        frame = frame.astype(type)
        return frame

    return _inner


def remove_borders(pixels, hard=False):
    """Removes the border of the frame"""

    def _inner(i, frame):
        H, W, _ = frame.shape
        if hard:
            frame = frame[pixels:-pixels, pixels:-pixels]
        else:
            frame[:pixels, :, :] = frame[H - pixels :, :, :] = frame[
                :, :pixels, :
            ] = frame[:, W - pixels :, :] = 0
        return frame

    return _inner


def remove_outside_petri(center, radius, hard=False):
    """Removes the part of the frame outside of an elipsis"""

    def _inner(i, frame):
        H, W, _ = frame.shape
        I, J = np.ogrid[:H, :W]
        dist_from_center = ((I - center[1]) / radius[1]) ** 2 + (
            (J - center[0]) / radius[0]
        ) ** 2
        mask = dist_from_center <= 1
        frame[~mask, :] = 0
        if hard:
            l, r = max(center[0] - radius[0], 0), min(center[0] + radius[0], W - 1)
            t, b = max(center[1] - radius[1], 0), min(center[1] + radius[1], H - 1)
            frame = frame[t:b, l:r]
        return frame

    return _inner


def annotate(labels, size=2, color=[255, 0, 0]):
    """Annotates the frames using labels"""

    def _inner(i, frame):
        label = labels.get(i, None)
        if label is not None:
            y, x = label
            frame[x - size : x + size, y - size : y + size] = np.array(
                color, dtype=np.uint8
            )
        return frame

    return _inner


def average(i, frames):
    """Computes the average frame"""
    base = frames[0][1].astype(np.uint32)
    for frame in frames[1:]:
        base += frame[1]
    return (base / len(frames)).astype(np.uint8)
