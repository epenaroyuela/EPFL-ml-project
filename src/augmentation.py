"""Compedium of functions to perform data augmentation"""
import numpy as np


def h_mirror_frame(i, frame):
    """Mirrors the frame horizontally"""
    return np.flip(frame, axis=1)


def h_mirror_label(i, label, size):
    """Mirrors the label horizontally"""
    return (size[0] - label[0], label[1])


def v_mirror_frame(i, frame):
    """Mirrors the frame vertically"""
    return np.flip(frame, axis=0)


def v_mirror_label(i, label, size):
    """Mirrors the frame vertically"""
    return (label[0], size[1] - label[1])


def rotate_90_frame(i, frame):
    """Rotates the frame 90 degrees"""
    return np.rot90(frame, 1, axes=(1, 0))


def rotate_90_label(i, label, size):
    """Rotates the label 90 degrees"""
    vec = (label[0] - size[0] / 2.0, label[1] - size[1] / 2.0)
    level = (-1.0 * vec[0], vec[1])
    return (int(level[0] + size[0] / 2.0), int(level[1] + size[1] / 2.0))


def rotate_180_frame(i, frame):
    """Rotates the frame 180 degrees"""
    return np.rot90(frame, 2, axes=(1, 0))


def rotate_180_label(i, label, size):
    """Rotates the label 180 degrees"""
    vec = (label[0] - size[0] / 2.0, label[1] - size[1] / 2.0)
    level = (-1.0 * vec[0], -1.0 * vec[1])
    return (int(level[0] + size[0] / 2.0), int(level[1] + size[1] / 2.0))


def rotate_270_frame(i, frame):
    """Rotates the frame 270 degrees"""
    return np.rot90(frame, 3, axes=(1, 0))


def rotate_270_label(i, label, size):
    """Rotates the label 270 degrees"""
    vec = (label[0] - size[0] / 2.0, label[1] - size[1] / 2.0)
    level = (vec[0], -1.0 * vec[1])
    return (int(level[0] + size[0] / 2.0), int(level[1] + size[1] / 2.0))
