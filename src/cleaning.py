import numpy as np

def select_channel(channel):
    def _inner(i, frame):
        frame = frame[:,:,channel:channel+1]
        return frame
    return _inner

# sets to 0 the borders of a one channel frame. 
# The width of the border is specified by n_pixels
def remove_borders(pixels):
    def _inner(i, frame):
        W, H, _ = frame.shape
        frame[:pixels, :, :] = frame[W-pixels:, :, :] = frame[:, :pixels, :] = frame[:, H-pixels:, :] = 0
        return frame
    return _inner

def remove_outside_petri(center, radius_i, radius_j):
    def _inner(i, frame):
        W, H, _ = frame.shape
        I, J = np.ogrid[:W, :H]
        dist_from_center = ((I - center[0])/radius_i)**2 + ((J-center[1])/radius_j)**2
        mask = dist_from_center <= 1
        frame[~mask, :] = 0
        return frame
    return _inner