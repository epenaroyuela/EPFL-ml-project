import copy
import itertools as it
import cv2

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
        assert captures
        length, W, H, C = captures[0]._length, captures[0]._W, captures[0]._H, captures[0]._C
        frames = captures[0]._length
        max_index = captures[0]._frames[-1][0] if captures[0]._length else 0
        for capture in captures[1:]:
            assert capture._W == W and capture._H == H and capture._C == C
            frames.extend([(i+max_index, frame) for i, frame in capture._frames])
            length = length + capture._length
            max_index = max_index + capture._frames[-1][0] if capture._length else 0
        return cls(length, W, H, C, frames)

    # Misc
    def clone(self):
        return Capture(self._length, self._W, self._H, self._C, copy.deepcopy(self._frames))

    def write(self, path, fps=50):
        if self._length:
            assert self._C == 3
            out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (self._W, self._H))
            for _, frame in self._frames:
                out.write(frame)
            out.release()

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
            assert frame_no in frames_dict
            return frames_dict[frame_no]
        else:
            assert frame_no >= 0 and frame_no < self._length
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
        assert not z or len(zip) == self._length
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
        assert not z or len(zip) == self._length
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
            assert frame.shape == (shape if shape is not None else (self._H, self._W, self._C))
            self._frames[i] = (self._frames[i][0], frame)
        if shape is not None:
            self._W, self._H, self._C = shape

    def rolling(self, func, window,  zip=None, acc=None, reverse=False, shape=None): # allow selecting position within window, allow lossless (fill ends with copies of end item), even window
        assert window % 2 == 1
        assert self._length >= window
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length
        half_window = window // 2
        q, lq = (self._frames[-window+1:], self._length - window) if reverse else (self._frames[:window-1], window - 1)
        r = range(half_window, self._length - half_window)
        for i in reversed(r) if reverse else r:
            if reverse:
                q.insert(0, self._frames[lq])
                lq = lq - 1
            else:
                q.append(self._frames[lq])
                lq = lq + 1
            if z and a:
                frame, acc = func(self._frames[i][0], q, zip[i], acc)
            elif z and not a:
                frame = func(self._frames[i][0], q, zip[i])
            elif not z and a:
                frame, acc = func(self._frames[i][0], q, acc)
            else:
                frame = func(self._frames[i][0], q)
            assert frame.shape == (shape if shape is not None else (self._H, self._W, self._C))
            self._frames[i] = (self._frames[i][0], frame)
            if reverse:
                q.pop()
            else:
                q.pop(0)
        tmp = self._frames[half_window:-half_window]
        self._length = len(tmp)
        self._frames = tmp
        if shape is not None:
            self._W, self._H, self._C = shape

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
        assert captures
        length, W, H, C = captures[0]._length, captures[0]._W, captures[0]._H, captures[0]._C
        for capture in captures:
            assert capture._W == W and capture._H == H and capture._C == C
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

    def write(self, path, fps=50):
        if self._length:
            assert self._C == 3
            out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (self._W, self._H))
            for _, frame in self._frames(reverse=False):
                out.write(frame)
            out.release()

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
            assert False
        else:
            assert frame_no >= 0 and frame_no < self._length
            it = self._frames(reverse=False)
            for _ in range(frame_no):
                next(it)
            return next(it)

    def frames_dict(self): # Not efficient
        class LazyDict:
            def __init__(self, frames):
                self._frames = frames
            def __getitem__(self, index):
                for i, frame in self._frames(reverse=False):
                    if i == index:
                        return frame
                assert False
            
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
        return iter(self._frames(reverse=reverse))

    # Operations
    def filter(self, func):
        _frames = self._frames
        def frames(reverse=False):
            for i, frame in _frames(reverse=reverse):
                if func(i, frame):
                    yield i, frame
        len = 0
        for _ in frames(reverse=False):
            len = len + 1
        self._length = len
        self._frames = frames

    def extract(self, func):
        return iter((func(i, frame) for i, frame in self._frames(reverse=False)))

    def foreach(self, func, zip=None, acc=None, reverse=False):
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length
        for i, frame in self._frames(reverse=reverse):
            if z and a:
                acc = func(i, frame, zip[i], acc)
            elif z and not a:
                func(i, frame, zip[i])
            elif not z and a:
                acc = func(i, frame, acc)
            else:
                func(i, frame)

    def apply(self, func, zip=None, acc=None, reverse=False, shape=None):
        apply_reverse = reverse
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length
        _frames = self._frames
        _length, _W, _H, _C = self._length, self._W, self._H, self._C
        def frames(reverse=False):
            def _same():
                for i, frame in _frames(reverse=reverse):
                    if z and a:
                        frame, acc = func(i, frame, zip[i], acc)
                    elif z and not a:
                        frame = func(i, frame, zip[i])
                    elif not z and a:
                        frame, acc = func(i, frame, acc)
                    else:
                        frame = func(i, frame)
                    assert frame.shape == (shape if shape is not None else (_H, _W, _C))
                    yield i, frame
            def _diff():
                accs = []
                for i, frame in _frames(reverse=apply_reverse):
                    if z:
                        _, acc = func(i, frame, zip[i], acc)
                    else:
                        _, acc = func(i, frame, acc)
                    accs.append(acc)
                j = _length - 1
                for i, frame in frames(reverse=reverse):
                    if z:
                        frame, _ = func(i, frame, zip[i], accs[j])
                    else:
                        frame, _ = func(i, frame, accs[j])
                    assert frame.shape == (shape if shape is not None else (_H, _W, _C))
                    yield i, frame
                    j = j - 1
            return _diff() if (a and apply_reverse != reverse) else _same()
        self._frames = frames
        if shape is not None:
            self._W, self._H, self._C = shape

    def rolling(self, func, window,  zip=None, acc=None, reverse=False, shape=None): # allow selecting position within window, allow lossless (fill ends with copies of end item), even window
        assert window % 2 == 1
        assert self._length >= window
        z, a = zip is not None, acc is not None
        assert not z or len(zip) == self._length
        half_window = window // 2
        q, lq = (self._frames[-window+1:], self._length - window) if reverse else (self._frames[:window-1], window - 1)
        r = range(half_window, self._length - half_window)
        for i in reversed(r) if reverse else r:
            if reverse:
                q.insert(0, self._frames[lq])
                lq = lq - 1
            else:
                q.append(self._frames[lq])
                lq = lq + 1
            if z and a:
                frame, acc = func(self._frames[i][0], q, zip[i], acc)
            elif z and not a:
                frame = func(self._frames[i][0], q, zip[i])
            elif not z and a:
                frame, acc = func(self._frames[i][0], q, acc)
            else:
                frame = func(self._frames[i][0], q)
            assert frame.shape == (shape if shape is not None else (self._H, self._W, self._C))
            self._frames[i] = (self._frames[i][0], frame)
            if reverse:
                q.pop()
            else:
                q.pop(0)
        tmp = self._frames[half_window:-half_window]
        self._length = len(tmp)
        self._frames = tmp
        if shape is not None:
            self._W, self._H, self._C = shape


    def __del__(self):
        self._frames = None

