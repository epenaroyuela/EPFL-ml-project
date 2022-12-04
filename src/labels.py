import numpy as np

# get labels from .txt file
# input: path of the file
# output: dictionary where key = slice number, value = true (i, j) coordinates of the worm
# TODO: why do we keep the first slice value?
def load_labels(path):
    file = open(path, 'r')
    slice = -1
    ret = {}
    for i, line in enumerate(file.readlines()):
        fields = line.split()
        if i == 0 or fields[7] == slice:
            continue
        true_i = float(fields[6])
        true_j = float(fields[5])
        slice = int(fields[7])
        ret[slice] = (true_i, true_j)
    return ret

def l2arr(label):
    return np.array(label, dtype=np.float32)

def l2i(label):
    return (int(label[0]), int(label[1]))

def larr2i(label):
    return label.astype(np.int32)