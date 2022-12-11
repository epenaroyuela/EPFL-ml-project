import numpy as np

# Metrics
"""
Calculates a custom accuracy, using ell infinity norm. 
For each frame, if estimated pos and labels are closer than distance small_radix,
we get a score of 1. Else if it's closer than big_radix, we get a score of 0.5. 
Otherwise, 0. Then, the accuracy is normalized between 0 and 1.
Input:
    true_positions: dict containing labels to the frames (some are missing)
    pred_positions: dict containing estimated positions to the frames
"""
def custom_accuracy(small_radix=10, big_radix=10):
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
    def _inner(tl, pl):
        def manhattan_dist(p1, p2):
            return abs((p1[0] - p2[0]) + (p1[1] - p2[1]))
        return manhattan_dist(tl, pl)
    return _inner

def evaluate(true_labels, pred_labels, metric_func):
    metric = 0.0
    labels =  true_labels.keys() & pred_labels.keys()
    for i in labels:
        metric += metric_func(true_labels[i], pred_labels[i])
    return len(labels), metric / len(labels)
