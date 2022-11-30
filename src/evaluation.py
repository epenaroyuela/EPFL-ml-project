import numpy as np

"""
Calculates a custom accuracy, using ell infinity norm. 
For each frame, if estimated pos and labels are closer than distance small_radix,
we get a score of 1. Else if it's closer than big_radix, we get a score of 0.5. 
Otherwise, 0. Then, the accuracy is normalized between 0 and 1.
Input:
    labels: dict containing labels to the frames (some are missing)
    pos_hat: dict containing estimated pos to the frames
"""
def custom_accuracy(labels, pos_hat, small_radix=10, big_radix=10):
    def ell_inf_dist(p1, p2):
        return max(np.abs(p1[0] - p2[0]), np.abs(p1[1] - p2[1]))
    acc = 0
    for t in labels:
        if t in pos_hat:
            dist = ell_inf_dist(labels[t], pos_hat[t])
            if dist <= small_radix:
                acc += 1
            elif dist <= big_radix:
                acc += 0.5
    return acc / len(labels)