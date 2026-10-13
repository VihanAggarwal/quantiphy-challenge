"""Lab focal-length audit (test inputs only): every depth_info entry that names a ball of known size (stated prior
or a standard ball) is paired with a precise pixel measurement of that ball on the frame of the entry's time
(colour segmentation + ellipse fit, ballmeas.py) in the o/s/x renders. Implied focal length:
   f = minor_axis_px * Z_c / D,  Z_c = r_c * cos(theta)  (a sphere's minor image axis = f D / Z_c)
under two depth conventions: r_c = r (depth_info = range to the ball centre) and r_c = r + D/2 (front surface)."""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from qp.data import load_test
import ballmeas as BM

DIAM = {"tennis": 0.067, "pingpong": 0.040, "red": 0.070, "basketball": 0.232, "soccer": 0.175, "yoga": 0.522}
# event-specific identities of generic names (from the events' own priors / questions)
GENERIC = {"captured_0029": {"ball": "tennis"}, "captured_0030": {"ball": "red"}, "captured_0028": {"ball": "pingpong"},
           "captured_0039": {"ball": "pingpong"}, "captured_0040": {"ball": "pingpong"},
           "captured_0031": {"white_ball": "pingpong"}, "captured_0032": {"ping_pong_ball": "pingpong"},
           "captured_0038": {"white_ball": "pingpong"}, "captured_0054a": {"orange_ball": "basketball"},
           "captured_0054b": {"orange_ball": "basketball"}, "captured_0013": {"ball": "tennis"}}


def ball_class(event, name):
    n = name.lower()
    g = GENERIC.get(event, {})
    for k, v in g.items():
        if n == k:
            return v
    for k, c in (("tennis", "tennis"), ("ping_?pong|ping pong|pingpong", "pingpong"), ("(^|_)red_", "red"),
                 ("basketball", "basketball"), ("soccer", "soccer"), ("yoga", "yoga")):
        if re.search(k, n):
            return c
    return None


def treal_to_frame(t):
    # capture time (25 fps clock) -> released 24 fps video frame (frames dropped after video frames 11/35/59)
    k = int(round(t * 25))
    n = k - (k >= 13) - (k >= 38) - (k >= 63)
    return max(n, 0)


def parse_depth(s):
    out = []
    for line in str(s).split("\n"):
        m = re.search(r"distance_([A-Za-z_ ]+?)_camera\s*=\s*([0-9.]+)", line)
        if not m:
            continue
        tm = re.search(r"t\s*=\s*([0-9.]+)", line)
        val = float(m.group(2))
        if val > 50:   # typo like 8420m
            continue
        out.append((m.group(1).strip(), float(tm.group(1)) if tm else None, val))
    return out


def boxes(rec, obj_name, scale):
    """All Claude boxes of tracks whose object matches obj_name (normalised), in 1280 px: {frame: box}."""
    p = json.loads(rec["raw_text"]); key = re.sub(r"[^a-z]", "", obj_name.lower())
    res = {}
    for q in p["questions"]:
        for tr in q["tracks"]:
            on = re.sub(r"[^a-z]", "", tr["object"].lower())
            if not (on == key or key in on or on in key):
                continue
            for o in tr["obs"]:
                b = o.get("box")
                if b:
                    res.setdefault(o["frame"], []).append([x / scale for x in b])
                elif o.get("point"):
                    pt = [x / scale for x in o["point"]]
                    res.setdefault(o["frame"], []).append(None if True else pt)
    return {k: [b for b in v if b is not None] for k, v in res.items() if any(b is not None for b in v)}


def box_at(bx, n):
    if not bx:
        return None, None
    fr = np.array(sorted(bx)); i = int(np.argmin(np.abs(fr - n)))
    b = np.median(np.array(bx[fr[i]]), axis=0)
    return list(b), int(abs(fr[i] - n))


def main():
    T = load_test()
    T = T[T.video_source == "lab"]
    T["event"] = T.video_id.str.replace(r"^(captured_\d+[ab]?)[sxX]?$", r"\1", regex=True)
    rows = []
    recdir = ROOT / "runs/test_v1_high_854/test/records"
    for ev, g in T.groupby("event"):
        if not (recdir / f"{ev}.json").exists():
            continue
        rec = json.load(open(recdir / f"{ev}.json"))
        scale = float(rec["meta"]["scale"])
        depth = parse_depth(g.depth_info.iloc[0])
        renders = sorted(g.video_id.unique())
        for name, t, r in depth:
            cls = ball_class(ev, name)
            if cls is None:
                continue
            bx = boxes(rec, name.replace("_", " "), scale)
            if not bx:
                # try the class word
                bx = boxes(rec, {"pingpong": "ping pong", "tennis": "tennis"}.get(cls, cls), scale)
            ts = [t] if t is not None else [0.5, 1.0, 1.5]
            for tt in ts:
                n = treal_to_frame(tt)
                b, gap = box_at(bx, n)
                if b is None:
                    rows.append(dict(event=ev, obj=name, cls=cls, t=tt, r=r, why="nobox")); continue
                for v in renders:
                    m = BM.measure(v, n, tuple(b), cls, debug_path=HERE / "meas" / f"{v}_{name}_{n}.png")
                    rows.append(dict(event=ev, video=v, obj=name, cls=cls, t=tt, frame=n, r=r, box_gap=gap, **m))
    D = pd.DataFrame(rows)
    D.to_csv(HERE / "out/f_audit_raw.csv", index=False)
    print(D.groupby(["event", "obj"]).size())


if __name__ == "__main__":
    main()
