

# ---- measurement helpers (deterministic; check their output on overlays before trusting it) ----
def background(n=25, i0=0, i1=None):
    """median of n frames spread over [i0, i1): the static background of a fixed camera (BGR uint8)"""
    i1 = N if i1 is None else min(int(i1), N)
    idx = np.unique(np.linspace(int(i0), max(int(i0), i1 - 1), int(n)).astype(int))
    return np.median(np.stack([frame(i) for i in idx]), axis=0).astype(np.uint8)


def motion_mask(i, bg=None, thr=30, open_px=3, close_px=7):
    """bool mask of pixels of frame i that differ from the background bg (default: background()) by > thr"""
    bg = background() if bg is None else bg
    d = cv2.absdiff(frame(i), bg).max(axis=2)
    m = (d > thr).astype(np.uint8)
    if open_px:
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((open_px, open_px), np.uint8))
    if close_px:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((close_px, close_px), np.uint8))
    return m.astype(bool)


def color_mask(img, lo, hi, space="hsv"):
    """bool mask of pixels with lo <= value <= hi per channel (space 'hsv' (OpenCV H 0-179) or 'bgr')"""
    im = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) if space == "hsv" else img
    return cv2.inRange(im, np.array(lo, np.uint8), np.array(hi, np.uint8)) > 0


def blobs(mask, min_area=20):
    """connected components of a bool mask, largest first: dicts cx, cy (centroid), x0, y0, x1, y1, w, h, area"""
    n, lab, st, cen = cv2.connectedComponentsWithStats(np.asarray(mask, np.uint8), 8)
    out = []
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a >= min_area:
            out.append(dict(cx=float(cen[k][0]), cy=float(cen[k][1]), x0=int(x), y0=int(y), x1=int(x + w - 1),
                            y1=int(y + h - 1), w=int(w), h=int(h), area=int(a)))
    return sorted(out, key=lambda b: -b["area"])


def track_motion(i0, i1, start_xy, bg=None, thr=30, min_area=20, max_jump=None):
    """follow one moving object: per frame i0..i1-1, the motion blob nearest the previous position (starting at
    start_xy). Returns a list of dicts i, t, cx, cy, w, h (None entries where nothing was found)."""
    bg = background() if bg is None else bg
    px, py = map(float, start_xy)
    out = []
    for i in range(int(i0), min(int(i1), N)):
        bs = blobs(motion_mask(i, bg, thr), min_area)
        if bs:
            b = min(bs, key=lambda b: (b["cx"] - px) ** 2 + (b["cy"] - py) ** 2)
            if max_jump is None or math.hypot(b["cx"] - px, b["cy"] - py) <= max_jump:
                px, py = b["cx"], b["cy"]
                out.append(dict(i=i, t=i / FPS, cx=b["cx"], cy=b["cy"], w=b["w"], h=b["h"]))
                continue
        out.append(None)
    return out


def track_template(i0, i1, box, search=60):
    """template tracking: box = (x0, y0, x1, y1) of the object in frame i0; per frame the best normalised-correlation
    match within +-search px of the previous position. Returns dicts i, t, cx, cy, score."""
    x0, y0, x1, y1 = map(int, box)
    tpl = frame(i0, gray=True)[y0:y1 + 1, x0:x1 + 1]
    th, tw = tpl.shape
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    for i in range(int(i0), min(int(i1), N)):
        g = frame(i, gray=True)
        sx0, sy0 = max(0, int(cx - tw / 2 - search)), max(0, int(cy - th / 2 - search))
        sx1, sy1 = min(W, int(cx + tw / 2 + search)), min(H, int(cy + th / 2 + search))
        win = g[sy0:sy1, sx0:sx1]
        if win.shape[0] < th or win.shape[1] < tw:
            out.append(None)
            continue
        r = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED)
        _, sc, _, loc = cv2.minMaxLoc(r)
        cx, cy = sx0 + loc[0] + tw / 2, sy0 + loc[1] + th / 2
        out.append(dict(i=i, t=i / FPS, cx=float(cx), cy=float(cy), score=float(sc)))
    return out


def focal_from_hfov(hfov_deg):
    """focal length in px for this frame width and a horizontal field of view in degrees"""
    return (W / 2) / math.tan(math.radians(hfov_deg) / 2)


def lab_focal():
    """lab camera focal length in px (~711 px at 1280 px width)"""
    return 711.0 * W / 1280.0


def backproject(u, v, dist, f, cx=None, cy=None, mode="range"):
    """3D camera-frame point (x right, y down, z forward) of pixel (u, v) at distance dist: mode 'range' = Euclidean
    camera-to-point distance (ToF / Blender depth_info), 'z' = depth along the optical axis"""
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    ray = np.array([(u - cx) / f, (v - cy) / f, 1.0])
    return ray * (dist / np.linalg.norm(ray) if mode == "range" else dist)


def dist3d(p, q):
    return float(np.linalg.norm(np.asarray(p, float) - np.asarray(q, float)))


def px_dist(a, b):
    return float(math.hypot(a[0] - b[0], a[1] - b[1]))


def speeds(points, fps=None, kind="backward"):
    """speed magnitudes from a list of positions (any units) at consecutive frames: 'backward' v[i] = |p[i]-p[i-1]|*fps
    (Blender convention), 'forward' v[i] = |p[i+1]-p[i]|*fps (lab convention), 'central'. NaN where undefined."""
    fps = FPS if fps is None else fps
    p = np.asarray(points, float)
    v = np.full(len(p), np.nan)
    if kind == "backward":
        v[1:] = np.linalg.norm(np.diff(p, axis=0), axis=-1) * fps
    elif kind == "forward":
        v[:-1] = np.linalg.norm(np.diff(p, axis=0), axis=-1) * fps
    else:
        v[1:-1] = np.linalg.norm(p[2:] - p[:-2], axis=-1) * fps / 2
    return v


def smooth(x, k=5):
    """moving average with window k (odd), edges shrink; NaN-safe"""
    x = np.asarray(x, float)
    h = int(k) // 2
    return np.array([np.nanmean(x[max(0, i - h):i + h + 1]) for i in range(len(x))])


def fit_line_track(track, deg=2):
    """least-squares polynomial fit (deg) of cx(t) and cy(t) over the non-None entries of a track; returns
    (fx, fy) numpy poly1d functions of time (use their derivatives for smooth velocities)"""
    pts = [p for p in track if p]
    t = np.array([p["t"] for p in pts]); x = np.array([p["cx"] for p in pts]); y = np.array([p["cy"] for p in pts])
    return np.poly1d(np.polyfit(t, x, deg)), np.poly1d(np.polyfit(t, y, deg))
