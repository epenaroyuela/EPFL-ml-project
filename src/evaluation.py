import numpy as np

"""
Calculates a custom accuracy, using ell infinity norm. 
For each frame, if estimated pos and labels are closer than distance small_radix,
we get a score of 1. Else if it's closer than big_radix, we get a score of 0.5. 
Otherwise, 0. Then, the accuracy is normalized between 0 and 1.
Input:
    true_positions: dict containing labels to the frames (some are missing)
    pred_positions: dict containing estimated positions to the frames
"""
def custom_accuracy(true_positions, pred_positions, small_radix=10, big_radix=10):
    def ell_inf_dist(p1, p2):
        return max(np.abs(p1[0] - p2[0]), np.abs(p1[1] - p2[1]))
    target = true_positions.keys() & pred_positions.keys()
    acc = 0.0
    for frame_i in target:
        dist = ell_inf_dist(true_positions[frame_i], pred_positions[frame_i])
        if dist <= small_radix:
            acc += 1
        elif dist <= big_radix:
            acc += 0.5
    return acc / len(target)


def mean_distance(true_positions, pred_positions):
    def manhattan_dist(p1, p2):
        return abs((p1[0] - p2[0]) + (p1[1] - p2[1]))
    target = true_positions.keys() & pred_positions.keys()
    dist = 0.0
    for frame_i in target:
        dist += manhattan_dist(true_positions[frame_i], pred_positions[frame_i])
    return dist / len(target)