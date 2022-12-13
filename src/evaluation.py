"""Evaluation function plus compedium of various metrics"""
import numpy as np


def custom_accuracy(small_radix=10, big_radix=10):
    """Custom accuracy, using ell infinity norm. The estimation obtains 1 if it is closer
    than 'small_radix' and 0.5 is it is closer than 'big_radix', 0 otherwise"""

    def _inner(tl, pl):
        def ell_inf_dist(p1, p2):
            return max(np.abs(p1[0] - p2[0]), np.abs(p1[1] - p2[1]))

        tmp = ell_inf_dist(tl, pl)
        if tmp <= small_radix:
            return 1.0
        elif tmp <= big_radix:
            return 0.5
        return 0.0

    return _inner


def distance():
    """Manhattan distance"""

    def _inner(tl, pl):
        def manhattan_dist(p1, p2):
            return abs((p1[0] - p2[0]) + (p1[1] - p2[1]))

        return manhattan_dist(tl, pl)

    return _inner


def evaluate(true_labels, pred_labels, metric_func):
    """Evaluates function, for a given metric"""
    metric = 0.0
    labels = true_labels.keys() & pred_labels.keys()
    for i in labels:
        metric += metric_func(true_labels[i], pred_labels[i])
    return len(labels), metric / len(labels)
