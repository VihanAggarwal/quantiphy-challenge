import cv2
V = '/home/user/quantiphy-challenge/data/QuantiPhy/captured_0024%s.mp4'
_cache = {}
def load(tag):
    if tag not in _cache:
        cap = cv2.VideoCapture(V % tag); fr = []
        while True:
            ok, f = cap.read()
            if not ok: break
            fr.append(f)
        _cache[tag] = fr
    return _cache[tag]
