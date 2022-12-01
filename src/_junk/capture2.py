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
        if ret:
            length, W, H, C = cap.get(cv2.CAP_PROP_FRAME_COUNT), cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT), 3
            frames.append((0, frame))
            frame_no = 1
            ret, frame = cap.read()
            while ret:
                frames.append((frame_no, frame))
                frame_no = frame_no + 1
                ret, frame = cap.read()
        cap.release()
        if not ret:
            raise Exception("Couldn't read video file: " + path)
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
        return (i for i, _ in self._frames)
    
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
        return (func(i, frame) for i, frame in self._frames)

    def foreach(self, func, zip=None, acc=None, reverse=False):
        for i in reversed(range(self._length)) if reverse else range(self._length):
            if acc is not None:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        acc = func(self._frames[i][0], self._frames[i][1], zip[i], acc)
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        acc = func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None), acc)
                else:
                    acc = func(self._frames[i][0], self._frames[i][1], acc)
            else:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        func(self._frames[i][0], self._frames[i][1], zip[i])
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None))
                else:
                    func(self._frames[i][0], self._frames[i][1])

    def apply(self, func, zip=None, acc=None, reverse=False, shape=None):
        for i in reversed(range(self._length)) if reverse else range(self._length):
            if acc is not None:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame, acc = func(self._frames[i][0], self._frames[i][1], zip[i], acc)
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame, acc = func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None), acc)
                else:
                   frame, acc = func(self._frames[i][0], self._frames[i][1], acc)
            else:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame = func(self._frames[i][0], self._frames[i][1], zip[i])
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame = func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None))
                else:
                    frame = func(self._frames[i][0], self._frames[i][1])
            assert frame.shape == (shape if shape is not None else (self._W, self._H, self._C))
            self._frames[i] = (self._frames[i][0], frame)
        if shape is not None:
            self._W, self._H, self._C = shape


    def rolling(self, func, window, zip=None, acc=None, reverse=False, shape=None): # allow selecting position within window, allow lossless (fill ends with copies of end item), even window
        assert window % 2 == 1
        assert self._length >= window
        half_window = window // 2
        q, lq = (self._frames[-window:], self._length - window - 1) if reverse else (self._frames[:window], window)
        r = range(half_window, self._length - half_window)
        for i in reversed(r) if reverse else r:
            if acc is not None:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame, acc = func(self._frames[i][0], q, zip[i], acc)
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame, acc = func(self._frames[i][0], q, zip.get(self._frames[i][0], None), acc)
                else:
                   frame, acc = func(self._frames[i][0], q, acc)
            else:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame = func(self._frames[i][0], q, zip[i])
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame = func(self._frames[i][0], q, zip.get(self._frames[i][0], None))
                else:
                    frame = func(self._frames[i][0], q)
            assert frame.shape == (shape if shape is not None else (self._W, self._H, self._C))
            self._frames[i] = (self._frames[i][0], frame)
            if reverse:
                q.pop()
                q.insert(0, self._frames[lq])
                lq = lq - 1
            else:
                q.pop(0)
                q.append(self._frames[lq])
                lq = lq + 1
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
        if ret:
            length, W, H, C = cap.get(cv2.CAP_PROP_FRAME_COUNT), cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT), 3
        cap.release()
        if not ret:
            raise Exception("Couldn't read video file: " + path)

        def frames(reverse=False):
            def _ahead():
                cap = cv2.VideoCapture(path)
                frame_no = 1
                ret, frame = cap.read()
                while ret:
                    yield frame_no, frame
                    frame_no = frame_no + 1
                    ret, frame = cap.read()
                cap.release()
            def _reverse():
                cap = cv2.VideoCapture(path)
                frame_no = cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1
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
        return (i for i, _ in self._frames(reverse=False))
    
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
        _frames = self.frames
        def frames(reverse=False):
            for i, frame in _frames(reverse=reverse):
                if func(i, frame):
                    yield i, frame
        self._length = len(frames(reverse=False))
        self._frames = frames

    def extract(self, func):
        return (func(i, frame) for i, frame in self._frames(reverse=False))

    def foreach(self, func, zip=None, acc=None, reverse=False):
        foreach_reverse = reverse
        _frames = self.frames
        def frames(reverse=False):
            if reverse == foreach_reverse:
                if acc is not None:
                    if zip is not None:
                        if isinstance(zip, list):
                            assert len(zip) == self._length
                            acc = func(self._frames[i][0], self._frames[i][1], zip[i], acc)
                        elif isinstance(zip, dict):
                            assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                            acc = func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None), acc)
                    else:
                        acc = func(self._frames[i][0], self._frames[i][1], acc)
                else:
                    if zip is not None:
                        if isinstance(zip, list):
                            assert len(zip) == self._length
                            func(self._frames[i][0], self._frames[i][1], zip[i])
                        elif isinstance(zip, dict):
                            assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                            func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None))
                    else:
                        func(self._frames[i][0], self._frames[i][1])

    def apply(self, func, zip=None, acc=None, reverse=False, shape=None):
        for i in reversed(range(self._length)) if reverse else range(self._length):
            if acc is not None:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame, acc = func(self._frames[i][0], self._frames[i][1], zip[i], acc)
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame, acc = func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None), acc)
                else:
                   frame, acc = func(self._frames[i][0], self._frames[i][1], acc)
            else:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame = func(self._frames[i][0], self._frames[i][1], zip[i])
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame = func(self._frames[i][0], self._frames[i][1], zip.get(self._frames[i][0], None))
                else:
                    frame = func(self._frames[i][0], self._frames[i][1])
            assert frame.shape == (shape if shape is not None else (self._W, self._H, self._C))
            self._frames[i] = (self._frames[i][0], frame)
        if shape is not None:
            self._W, self._H, self._C = shape


    def rolling(self, func, window, zip=None, acc=None, reverse=False, shape=None): # allow selecting position within window, allow lossless (fill ends with copies of end item), even window
        assert window % 2 == 1
        assert self._length >= window
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
            if acc is not None:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame, acc = func(self._frames[i][0], q, zip[i], acc)
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame, acc = func(self._frames[i][0], q, zip.get(self._frames[i][0], None), acc)
                else:
                   frame, acc = func(self._frames[i][0], q, acc)
            else:
                if zip is not None:
                    if isinstance(zip, list):
                        assert len(zip) == self._length
                        frame = func(self._frames[i][0], q, zip[i])
                    elif isinstance(zip, dict):
                        assert set(zip.keys()).issubset(set(dict(self._frames).keys()))
                        frame = func(self._frames[i][0], q, zip.get(self._frames[i][0], None))
                else:
                    frame = func(self._frames[i][0], q)
            assert frame.shape == (shape if shape is not None else (self._W, self._H, self._C))
            self._frames[i] = (self._frames[i][0], frame)
            if reverse:
                q.pop()
            else:
                q.pop(0)
        if shape is not None:
            self._W, self._H, self._C = shape

    def __del__(self):
        self._frames = None
