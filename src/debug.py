import numpy as np
import matplotlib.pyplot as plt

def print_frame(single_channel=False):
    def _inner(i, frame, positions):
        W, H, C = frame.shape
        if single_channel:
            frame_p = np.zeros([W,H,3], dtype=np.int8)
            frame_p[:,:,0] = frame
            frame_p[:,:,1] = frame
            frame_p[:,:,2] = frame
            frame = frame_p

        if positions:
            true_pos, estimated_pos = positions
            t1, t2 = true_pos[0], true_pos[1]
            e1, e2 = estimated_pos[0], estimated_pos[1]
            frame[t1-2:t1+2, t2-2:t2+2] = np.array([0, 255, 0])
            frame[e1-2:e1+2, e2-2:e2+2] = np.array([255, 0, 0])

        plt.imshow(frame, cmap='viridis')
        plt.show()
    return _inner

