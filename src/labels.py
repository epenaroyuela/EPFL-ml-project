"""Compedium of functions to manipulate labels"""
import numpy as np


def load_labels(path):
    """Loads labels from a file into a dictionary"""
    file = open(path, "r")
    slice = -1
    ret = {}
    for i, line in enumerate(file.readlines()):
        fields = line.split()
        if i == 0 or fields[7] == slice:
            continue
        true_i = float(fields[5])
        true_j = float(fields[6])
        slice = int(fields[7])
        ret[slice] = (true_i, true_j)
    return ret


def map_labels(labels, func):
    """Maps a dictionary of labels using the given function"""
    return {k: func(v) for k, v in labels.items()}


def l2arr(label):
    """Converts label from tuple to array"""
    return np.array(label, dtype=np.float32)


def l2i(label):
    """Casts tuple label to int"""
    return (int(label[0]), int(label[1]))


def larr2i(label):
    """Casts array label to int"""
    return label.astype(np.int32)
