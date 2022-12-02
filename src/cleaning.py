import numpy as np

def select_channel(channel):
    def _inner(i, frame):
        frame = frame[:,:,channel:channel+1]
        return frame
    return _inner

# sets to 0 the borders of a one channel frame. 
# The width of the border is specified by n_pixels
def remove_borders(pixels, hard=False):
    def _inner(i, frame):
        H, W, _ = frame.shape
        if hard:
            frame = frame[pixels:-pixels, pixels:-pixels]
        else:
            frame[:pixels, :, :] = frame[H-pixels:, :, :] = frame[:, :pixels, :] = frame[:, W-pixels:, :] = 0
        return frame
    return _inner

def remove_outside_petri(center, radius, hard=False):
    def _inner(i, frame):
        H, W, _ = frame.shape
        I, J = np.ogrid[:H, :W]
        dist_from_center = ((I - center[1])/radius[1])**2 + ((J-center[0])/radius[0])**2
        mask = dist_from_center <= 1
        frame[~mask, :] = 0
        if hard:
            l, r = max(center[0]-radius[0], 0), min(center[0]+radius[0], W-1)
            t, b = max(center[1]-radius[1], 0), min(center[1]+radius[1], H-1)
            frame = frame[t:b, l:r]
        return frame
    return _inner