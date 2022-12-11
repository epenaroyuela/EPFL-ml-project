import numpy as np

def h_mirror_frame(i, frame):
    return np.flip(frame, axis=1)

def h_mirror_label(i, label, size):
    return (size[0] - label[0], label[1])

def v_mirror_frame(i, frame):
    return np.flip(frame, axis=0)

def v_mirror_label(i, label, size):
    return (label[0], size[1] - label[1])

def rotate_90_frame(i, frame):
    return np.rot90(frame, 1, axes=(1, 0))

def rotate_90_label(i, label, size):
    vec = (label[0] - size[0] / 2.0, label[1] - size[1] / 2.0)
    level = (-1.0 * vec[0], vec[1])
    return (int(level[0] + size[0] / 2.0), int(level[1] + size[1] / 2.0))

def rotate_180_frame(i, frame):
    return np.rot90(frame, 2, axes=(1, 0))

def rotate_180_label(i, label, size):
    vec = (label[0] - size[0] / 2.0, label[1] - size[1] / 2.0)
    level = (-1.0 * vec[0], -1.0 * vec[1])
    return (int(level[0] + size[0] / 2.0), int(level[1] + size[1] / 2.0))

def rotate_270_frame(i, frame):
    return np.rot90(frame, 3, axes=(1, 0))

def rotate_270_label(i, label, size):
    vec = (label[0] - size[0] / 2.0, label[1] - size[1] / 2.0)
    level = (vec[0], -1.0 * vec[1])
    return (int(level[0] + size[0] / 2.0), int(level[1] + size[1] / 2.0))