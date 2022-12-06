import copy
import itertools as it
import cv2

def _take(it, n):
    tmp = [next(it) for _ in range(n)]
    return it, tmp

def _skip(it, n):
    for _ in range(n):
        next(it)
    return it

class Capture:
    
    # Constructor
    def __init__(self, length, W, H, C, frames): # assume the parameters are correct
        self._length = length
        self._W = W
        self._H = H
        self._C = C
        self._frames = frames

    # Factories
    @classmethod
    def load(cls, path): # 'path' can be either a '.avi' or a wildcard for '.jpeg' images
        frames = []
        length, W, H, C = None, None, None, None
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            raise Exception("Couldn't read video file: " + path)
        else:
            length, W, H, C = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), 3
            frames.append((0, frame))
            frame_no = 1
            ret, frame = cap.read()
            while ret:
                frames.append((frame_no, frame))
                frame_no = frame_no + 1
                ret, frame = cap.read()
        cap.release()
        return cls(length, W, H, C, frames)

    @classmethod
    def concat(cls, captures):
        assert captures, "captures is empty"
        length, W, H, C = captures[0]._length, captures[0]._W, captures[0]._H, captures[0]._C
        frames = captures[0]._length
        max_index = captures[0]._frames[-1][0] if captures[0]._length else 0
        for capture in captures[1:]:
            assert capture._W == W and capture._H == H and capture._C == C, "({}, {}, {}) != ({}, {}, {})".format(capture._W, capture._H, capture._C, W, H, C)
            frames.extend([(i + max_index, frame) for i, frame in capture._frames])
            length = length + capture._length
            max_index = max_index + capture._frames[-1][0] if capture._length else 0
        return cls(length, W, H, C, frames)

    # Misc
    def clone(self):
        return Capture(self._length, self._W, self._H, self._C, copy.deepcopy(self._frames))

    def write(self, path, fps=50, reverse=False):
        if self._length:
            assert self._C == 3, "C != 3"
            out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (self._W, self._H))
            for _, frame in (reversed(self._frames) if reverse else self._frames):
                out.write(frame)
            out.release()

    def __str__(self):
        return "Capture[length = {}; shape = {}]".format(self._length, (self._W, self._H, self._C))

    # Getters
    def length(self):
        return self._length

    def W(self):
        return self._W

    def H(self):
        return self._H

    def C(self):
        return self._C
    
    def frame(self, frame_no, index=True):
        if index:
            frames_dict = dict(self._frames)
            assert frame_no in frames_dict, "{} not in frames".format(frame_no)
            return frames_dict[frame_no]
        else:
            assert frame_no >= 0 and frame_no < self._length, "{} out of range [{}, {}]".format(frame_no, 0, self._length)
            return self._frames[frame_no]

    def frames_dict(self):
        return dict(self._frames)

    # Index
    def index(self):
        return [i for i, _ in self._frames]
    
    def reset_index(self):
        self._frames = list(enumerate([frame for _, frame in self._frames]))

    # Iterators
    def frames(self, reverse=False):
        if reverse:
            return iter(reversed(self._frames))
        else:
            return iter(self._frames)

    # Operations
    def filter(self, func):
        tmp = [(i, frame) for i, frame in self._frames if func(i, frame)]
        self._length = len(tmp)
        self._frames = tmp

    def extract(self, func):
        return [func(i, frame) for i, frame in self._frames]

    def foreach(self, func, zip=None, acc=None, reverse=False):
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length, "len(zip) {} != {}".format(len(zip), self._length)
        r = range(self._length)
        for i in reversed(r) if reverse else r:
            if z and a:
                acc = func(self._frames[i][0], self._frames[i][1], zip[i], acc)
            elif z and not a:
                func(self._frames[i][0], self._frames[i][1], zip[i])
            elif not z and a:
                acc = func(self._frames[i][0], self._frames[i][1], acc)
            else:
                func(self._frames[i][0], self._frames[i][1])

    def apply(self, func, zip=None, acc=None, reverse=False, shape=None):
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length, "len(zip) {} != {}".format(len(zip), self._length)
        _shape = (shape[1], shape[0], shape[2]) if shape is not None else (self._H, self._W, self._C)
        r = range(self._length)
        for i in reversed(r) if reverse else r:
            if z and a:
                frame, acc = func(self._frames[i][0], self._frames[i][1], zip[i], acc)
            elif z and not a:
                frame = func(self._frames[i][0], self._frames[i][1], zip[i])
            elif not z and a:
                frame, acc = func(self._frames[i][0], self._frames[i][1], acc)
            else:
                frame = func(self._frames[i][0], self._frames[i][1])
            assert frame.shape == _shape, "{} != {}".format(frame.shape, _shape)
            self._frames[i] = (self._frames[i][0], frame)
        if shape is not None:
            self._W, self._H, self._C = _shape[1], _shape[0], _shape[2]

    def rolling(self, func, window,  zip=None, acc=None, reverse=False, shape=None): # allow selecting position within window, allow lossless (fill ends with copies of end item), even window
        assert window % 2 == 1, "window is not even"
        assert self._length >= window, "windos is too large, {} > {}".format(window, self._length)
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length, "len(zip) {} != {}".format(len(zip), self._length)
        _shape = (shape[1], shape[0], shape[2]) if shape is not None else (self._H, self._W, self._C)
        half_window = window // 2
        q, lq = (reversed(self._frames[-window+1:]), self._length - window) if reverse else (self._frames[:window-1], window - 1)
        r = range(half_window, self._length - half_window)
        for i in reversed(r) if reverse else r:
            q.append(self._frames[lq])
            lq = lq + (-1 if reverse else 1)
            if z and a:
                frame, acc = func(self._frames[i][0], q, zip[i], acc)
            elif z and not a:
                frame = func(self._frames[i][0], q, zip[i])
            elif not z and a:
                frame, acc = func(self._frames[i][0], q, acc)
            else:
                frame = func(self._frames[i][0], q)
            assert frame.shape == _shape, "{} != {}".format(frame.shape, _shape)
            self._frames[i] = (self._frames[i][0], frame)
            q.pop(0)
        tmp = self._frames[half_window:-half_window]
        self._length = self._length - 2 * half_window
        self._frames = tmp
        if shape is not None:
            self._W, self._H, self._C = _shape[1], _shape[0], _shape[2]

    # Destructor
    def __del__(self):
        self._frames = None




class LazyCapture:
    
    # Constructor
    def __init__(self, length, W, H, C, frames): # assume the parameters are correct
        self._length = length
        self._W = W
        self._H = H
        self._C = C
        self._frames = frames

    # Factories
    @classmethod
    def load(cls, path): # 'path' can be either a '.avi' or a wildcard for '.jpeg' images
        length, W, H, C = None, None, None, None
        cap = cv2.VideoCapture(path)
        ret, _ = cap.read()
        if not ret:
            cap.release()
            raise Exception("Couldn't read video file: " + path)
        else:
            length, W, H, C = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), 3
        cap.release()

        def frames(reverse=False):
            def _ahead():
                cap = cv2.VideoCapture(path)
                frame_no = 0
                ret, frame = cap.read()
                while ret:
                    yield frame_no, frame
                    frame_no = frame_no + 1
                    ret, frame = cap.read()
                cap.release()
            def _reverse():
                cap = cv2.VideoCapture(path)
                frame_no = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
                ret, frame = cap.read()
                while ret and frame_no >= 0:
                    yield frame_no, frame
                    frame_no = frame_no - 1
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
                    ret, frame = cap.read()
                cap.release()
            return _reverse() if reverse else _ahead()
        return cls(length, W, H, C, frames)

    @classmethod
    def concat(cls, captures):
        assert captures, "captures is empty"
        length, W, H, C = captures[0]._length, captures[0]._W, captures[0]._H, captures[0]._C
        for capture in captures[1:]:
            assert capture._W == W and capture._H == H and capture._C == C, "({}, {}, {}) != ({}, {}, {})".format(capture._W, capture._H, capture._C, W, H, C)
            length = length + capture._length
        def frames(reverse=False):
            def _ahead():
                curr_index, max_index = 0, 0
                for capture in captures:
                    curr_index = curr_index + max_index
                    max_index = 0
                    for i, frame in capture._frames(reverse=False):
                        max_index = i
                        yield curr_index + i, frame
            def _reverse():
                curr_indices = []
                curr_index, max_index = 0, 0
                for capture in captures:
                    curr_index = curr_index + max_index
                    curr_indices.append(curr_index)
                    max_index = 0
                    for i, _ in capture._frames(reverse=False):
                        max_index = i
                for capture, curr_index in reversed(zip(captures, curr_indices)):
                    for i, frame in capture._frames(reverse=True):
                        yield curr_index + i, frame
            return _reverse() if reverse else _ahead()
        return cls(length, W, H, C, frames)

    # Misc
    def clone(self):
        return Capture(self._length, self._W, self._H, self._C, self._frames)

    def write(self, path, fps=50, reverse=False):
        if self._length:
            assert self._C == 3, "C != 3"
            out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (self._W, self._H))
            for _, frame in self._frames(reverse=reverse):
                out.write(frame)
            out.release()

    def __str__(self):
        return "LazyCapture[length = {}; shape = {}]".format(self._length, (self._W, self._H, self._C))

    # Getters
    def length(self):
        return self._length

    def W(self):
        return self._W

    def H(self):
        return self._H

    def C(self):
        return self._C
    
    def frame(self, frame_no, index=True): # Not efficient
        if index:
            for i, frame in self._frames(reverse=False):
                if i == frame_no:
                    return frame
            assert False, "{} not in frames".format(frame_no)
        else:
            assert frame_no >= 0 and frame_no < self._length, "{} out of range [{}, {}]".format(frame_no, 0, self._length)
            it = self._frames(reverse=False)
            _skip(it, frame_no)
            return next(it)

    def frames_dict(self): # Not efficient
        class LazyDict:
            def __init__(self, frames):
                self._frames = frames
            def __getitem__(self, index):
                for i, frame in self._frames(reverse=False):
                    if i == index:
                        return frame
                raise KeyError
        return LazyDict(self._frames)

    # Index
    def index(self):
        return iter((i for i, _ in self._frames(reverse=False)))
    
    def reset_index(self):
        _frames = self.frames
        def frames(reverse=False):
            def _ahead():
                frame_no = 0
                for _, frame in _frames(reverse=False):
                    yield frame_no, frame
                    frame_no = frame_no + 1
            def _reverse():
                frame_no = self._length - 1
                for _, frame in _frames(reverse=True):
                    yield frame_no, frame
                    frame_no = frame_no - 1
            return _reverse() if reverse else _ahead()
        self._frames = frames

    # Iterators
    def frames(self, reverse=False):
        return self._frames(reverse=reverse)

    # Operations
    def filter(self, func):
        _frames = self._frames
        def frames(reverse=False):
            for i, frame in _frames(reverse=reverse):
                if func(i, frame):
                    yield i, frame
        _length = 0
        for _ in frames(reverse=False):
            _length = _length + 1
        self._length = _length
        self._frames = frames

    def extract(self, func):
        return iter((func(i, frame) for i, frame in self._frames(reverse=False)))

    def foreach(self, func, zip=None, acc=None, reverse=False):
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length, "len(zip) {} != {}".format(len(zip), self._length)
        j = (self._length - 1 if reverse else 0)
        for i, frame in self._frames(reverse=reverse):
            if z and a:
                acc = func(i, frame, zip[j], acc)
            elif z and not a:
                func(i, frame, zip[j])
            elif not z and a:
                acc = func(i, frame, acc)
            else:
                func(i, frame)
            j = j + (-1 if reverse else 1)

    def apply(self, func, zip=None, acc=None, reverse=False, shape=None):
        apply_reverse = reverse
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length, "len(zip) {} != {}".format(len(zip), self._length)
        _shape = (shape[1], shape[0], shape[2]) if shape is not None else (self._H, self._W, self._C)
        _frames, _length = self._frames, self._length
        def frames(reverse=False):
            def _same():
                _acc = acc
                j = (_length - 1 if reverse else 0)
                for i, frame in _frames(reverse=reverse):
                    if z and a:
                        frame, _acc = func(i, frame, zip[j], _acc)
                    elif z and not a:
                        frame = func(i, frame, zip[j])
                    elif not z and a:
                        frame, _acc = func(i, frame, _acc)
                    else:
                        frame = func(i, frame)
                    assert frame.shape == _shape, "{} != {}".format(frame.shape, _shape)
                    yield i, frame
                    j = j + (-1 if reverse else 1)
            def _diff():
                _acc = acc
                if a:
                    accs = []
                    j = (_length - 1 if reverse else 0)
                    for i, frame in _frames(reverse=apply_reverse):
                        if z:
                            _, _acc = func(i, frame, zip[j], _acc)
                        else:
                            _, _acc = func(i, frame, _acc)
                        accs.append(_acc)
                        j = j + (-1 if reverse else 1)
                k = _length - 1
                j = (_length - 1 if reverse else 0)
                for i, frame in _frames(reverse=reverse):
                    if z and a:
                        frame, _ = func(i, frame, zip[j], accs[k])
                    elif z and not a:
                        frame = func(i, frame, zip[j])
                    elif not z and a:
                        frame, _ = func(i, frame, accs[k])
                    else:
                        frame = func(i, frame)
                    assert frame.shape == _shape, "{} != {}".format(frame.shape, _shape)
                    yield i, frame
                    k = k - 1
                    j = j + (-1 if reverse else 1)
            return _diff() if apply_reverse != reverse else _same()
        self._frames = frames
        if shape is not None:
            self._W, self._H, self._C = _shape[1], _shape[0], _shape[2]

    def rolling(self, func, window,  zip=None, acc=None, reverse=False, shape=None): # allow selecting position within window, allow lossless (fill ends with copies of end item), even window
        rolling_reverse = reverse
        assert window % 2 == 1, "window is not even"
        assert self._length >= window, "windos is too large, {} > {}".format(window, self._length)
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length, "len(zip) {} != {}".format(len(zip), self._length)
        _shape = (shape[1], shape[0], shape[2]) if shape is not None else (self._H, self._W, self._C)
        _frames, _length = self._frames, self._length
        half_window = window // 2
        def frames(reverse=False):
            def _same():
                _acc = acc
                q, it = _take(_frames(reverse=reverse), window - 1)
                j = (_length - half_window if reverse else half_window)
                for i, frame in it:
                    q.append(frame)
                    j = j + (-1 if reverse else 1)
                    if z and a:
                        frame, _acc = func(i, q, zip[j], _acc)
                    elif z and not a:
                        frame = func(i, q, zip[j])
                    elif not z and a:
                        frame, _acc = func(i, q, _acc)
                    else:
                        frame = func(i, q)
                    assert frame.shape == _shape, "{} != {}".format(frame.shape, _shape)
                    yield i, frame
                    q.pop(0)
                    j = j + (-1 if reverse else 1)
            def _diff():
                _acc = acc
                if a:
                    accs = []
                    q, it = _take(_frames(reverse=rolling_reverse), window - 1)
                    j = (_length - half_window if reverse else half_window)
                    for i, frame in it:
                        q.append(frame)
                        j = j + (-1 if reverse else 1)
                        if z:
                            _, _acc = func(i, q, zip[j], _acc)
                        else:
                            _, _acc = func(i, q, _acc)
                        accs.append(_acc)
                        q.pop(0)
                        j = j + (-1 if reverse else 1)
                q, it = _take(_frames(reverse=reverse), window - 1)
                k = _length - 2 * half_window - 1
                j = (_length - 1 if reverse else 0)
                for i, frame in _frames(reverse=reverse):
                    q.append(frame)
                    if z and a:
                        frame, _ = func(i, q, zip[j], accs[k])
                    elif z and not a:
                        frame = func(i, q, zip[j])
                    elif not z and a:
                        frame, _ = func(i, q, accs[k])
                    else:
                        frame = func(i, q)
                    assert frame.shape == _shape, "{} != {}".format(frame.shape, _shape)
                    yield i, frame
                    q.pop(0)
                    k = k - 1
                    j = j + (-1 if reverse else 1)
            return _diff() if rolling_reverse != reverse else _same()
        self._length = self._length - 2 * half_window
        self._frames = frames
        if shape is not None:
            self._W, self._H, self._C = _shape[1], _shape[0], _shape[2]

    def __del__(self):
        self._frames = None
