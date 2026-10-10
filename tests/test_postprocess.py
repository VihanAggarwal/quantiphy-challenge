"""qp/postprocess.py and scripts/postprocess.py: twin / render / stated-fact rules.

Unit tests run on synthetic frames and question tables; the last tests apply the rules to the real
test set when data/QuantiPhy is present (skipped otherwise)."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest

from qp import postprocess as P

ROOT = Path(__file__).resolve().parents[1]


# ----------------------------------------------------------------------------- helpers

def _df(rows):
    """Question table from (qid, video_id, question, prior, depth_info[, category]) tuples."""
    out = []
    for r in rows:
        qid, vid, q, prior, depth = r[:5]
        cat = r[5] if len(r) > 5 else ("S3" if depth else "S2")
        src = "lab" if vid.startswith("captured") else ("segmentation" if vid.endswith("_segmented") else "simulation")
        out.append(dict(qid=qid, video_id=vid, question=q, prior=prior, depth_info=depth, category=cat,
                        video_source=src, video_type=f"V{cat[1]}MS", inference_type=cat[0] * 2, video_path=""))
    df = pd.DataFrame(out)
    from qp.data import target_unit
    df["target_unit"] = df.question.map(target_unit)
    return df


def _pred(df, value=1.0):
    return pd.Series(value, index=df.qid.astype(int), dtype=float)


def _scene(t: float, n: int = 96, shade: int = 0, bg: bool = True) -> np.ndarray:
    """Textured background (or plain white) with an off-centre orange box moving right."""
    if bg:
        yy, xx = np.mgrid[0:n, 0:n]
        img = np.stack([(xx * 2) % 256, (yy * 3) % 256, ((xx + yy) * 5) % 256], axis=2).astype(np.uint8)
        img[40:56, :] = (40, 160, 40)
    else:
        img = np.full((n, n, 3), 255, np.uint8)
    x0 = 10 + int(30 * t)
    img[14:34, x0:x0 + 22] = np.clip(np.array([30, 120, 230]) + shade, 0, 255)
    return img


def _video(path: Path, frames: list[np.ndarray], fps: float = 10.0) -> None:
    h, w = frames[0].shape[:2]
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for f in frames:
        vw.write(f)
    vw.release()


@pytest.fixture
def aligned_twins(monkeypatch):
    """Every twin pair counts as pixel-aligned (rule logic without video files)."""
    monkeypatch.setattr(P.FrameCache, "twin", lambda self, *a: {"status": "aligned"})


# ----------------------------------------------------------------------------- ids and text

def test_ids_and_question_normalisation():
    assert P.twin_original("simulation_0010_segmented") == "simulation_0010"
    assert P.twin_original("simulation_0010") is None
    assert P.lab_base("captured_0013s") == "captured_0013" and P.lab_base("captured_0010X") == "captured_0010"
    assert P.lab_base("captured_0034bx") == "captured_0034b" and P.lab_base("captured_0013") is None
    assert P.base_id("internet_0003_segmented") == "internet_0003" and P.base_id("captured_0031x") == "captured_0031"
    assert P.norm_question("What is the speed at 1.0s?") == P.norm_question("what is the  speed at 1s")
    assert P.exact_text("total height = 90 cm") == P.exact_text("total height = 90cm")
    assert P.exact_text("money width = 7.5cm") != P.exact_text("monopoly money width = 7.5cm")


# ----------------------------------------------------------------------------- frames

def test_twin_alignment_aligned_rotated_unknown():
    ts = (0.0, 0.5, 1.0)
    orig = [_scene(t) for t in ts]
    seg = [_scene(t, bg=False) for t in ts]
    a = P.twin_alignment(orig, seg)
    assert a["status"] == "aligned" and a["transform"] == "identity"
    # a re-render with different shading of the object is still the same view (edge score)
    assert P.twin_alignment(orig, [_scene(t, bg=False, shade=-80) for t in ts])["status"] == "aligned"
    # the original is the segmented view rotated by 90 degrees
    r = P.twin_alignment([np.ascontiguousarray(np.rot90(f)) for f in orig], seg)
    assert r["status"] == "rotated" and r["transform"] == "rot270"
    # mirrored original
    assert P.twin_alignment([np.ascontiguousarray(f[:, ::-1]) for f in orig], seg)["status"] == "rotated"
    # nothing kept in the segmented frames: cannot tell
    blank = [np.full((96, 96, 3), 255, np.uint8)] * 3
    assert P.twin_alignment(orig, blank)["status"] == "unknown"
    # frames of a portrait original against a landscape segmented clip: only a rotation fits
    wide = [np.ascontiguousarray(np.concatenate([_scene(t), _scene(t)], axis=1)) for t in ts]
    wide_seg = [np.ascontiguousarray(np.concatenate([_scene(t, bg=False)] * 2, axis=1)) for t in ts]
    assert P.twin_alignment(wide, wide_seg)["status"] == "aligned"
    assert P.twin_alignment([np.ascontiguousarray(np.rot90(f)) for f in wide], wide_seg)["status"] == "rotated"


def test_read_frames_keeps_positions_when_a_frame_fails(tmp_path, monkeypatch):
    path = tmp_path / "clip.mp4"
    _video(path, [_scene(t) for t in np.linspace(0, 1, 12)])
    frames, n = P.read_frames(str(path), (0.0, 0.5, 1.0))
    assert n == 12 and len(frames) == 3 and all(f is not None for f in frames)
    real = cv2.VideoCapture

    class Flaky:                                       # frames 4-6 (around the middle position) unreadable
        def __init__(self, p):
            self.cap, self.pos = real(p), 0

        def set(self, prop, value):
            self.pos = int(value)
            return self.cap.set(prop, value)

        def read(self):
            return (False, None) if 4 <= self.pos <= 6 else self.cap.read()

        def __getattr__(self, name):
            return getattr(self.cap, name)

    monkeypatch.setattr(cv2, "VideoCapture", Flaky)
    frames, _ = P.read_frames(str(path), (0.0, 0.5, 1.0))
    assert len(frames) == 3 and frames[1] is None and frames[0] is not None and frames[2] is not None
    # the last frame still pairs with the other clip's last frame (not with its middle one)
    seg = [_scene(t, bg=False) for t in (0.0, 0.5, 1.0)]
    assert P.twin_alignment(frames, seg)["status"] == "aligned"
    assert P.FrameCache(None).thumbs("clip", str(path)) is None   # thumbnails need all three frames


def test_foreground_uses_dominant_colour_not_border():
    img = np.zeros((100, 160, 3), np.uint8)          # black background (SAM-masked internet clip) ...
    img[:3] = 200
    img[-3:] = 200                                    # ... whose kept road edges run along the border
    img[40:60, 50:90] = (0, 0, 255)
    m = P._foreground(img)
    assert m is not None and m[50, 70] and not m[80, 20]


def test_frame_similarity_and_pairs():
    th = {v: {"th": P.thumbnails([_scene(t) for t in (0, 0.5, 1)]), "ar": 1.0, "n": 10}
          for v in ("simulation_0001", "simulation_0002")}
    th["simulation_0003"] = {"th": P.thumbnails([np.rot90(_scene(t)).copy() for t in (0, 0.5, 1)]), "ar": 1.0, "n": 10}
    th["simulation_0001_segmented"] = dict(th["simulation_0001"])       # same base: never a frame link
    s = P.frame_similarity(th["simulation_0001"]["th"], th["simulation_0002"]["th"])
    assert s["ncc"] > 0.999 and s["aligned_mad"] < 0.01
    pairs = {(a, b) for a, b, _ in P.frame_pairs(th)}
    assert ("simulation_0001", "simulation_0002") in pairs
    assert not any("simulation_0003" in p for p in pairs)
    assert ("simulation_0001", "simulation_0001_segmented") not in pairs


# ----------------------------------------------------------------------------- twin rule

def test_twin_rule_on_videos_with_cache(tmp_path, monkeypatch):
    vids = tmp_path / "videos"
    vids.mkdir()
    ts = np.linspace(0, 1, 12)
    _video(vids / "simulation_0001.mp4", [_scene(t) for t in ts])
    _video(vids / "simulation_0001_segmented.mp4", [_scene(t, bg=False) for t in ts])
    _video(vids / "simulation_0002.mp4", [np.ascontiguousarray(np.rot90(_scene(t))) for t in ts])
    _video(vids / "simulation_0002_segmented.mp4", [_scene(t, bg=False) for t in ts])
    q = "What is the length of the orange box in meters?"
    df = _df([(1, "simulation_0001", q, "length of the car = 4.5m", ""),
              (2, "simulation_0001_segmented", q.replace("box in", "box  in"), "length of the car = 4.5m", ""),
              (3, "simulation_0001_segmented", "What is the speed of the box at 1.0s in m/s?",
               "length of the car = 4.5m", ""),
              (4, "simulation_0001", "What is the speed of the box at 1s in m/s?", "length of the car = 4.6m", ""),
              (5, "simulation_0001_segmented", "What is the speed of the box at 1s in m/s?",
               "length of the car = 4.5m", ""),     # same question, different prior: not copied
              (6, "simulation_0002", q, "length of the car = 4.5m", ""),
              (7, "simulation_0002_segmented", q, "length of the car = 4.5m", ""),
              (8, "simulation_0003_segmented", q, "length of the car = 4.5m", ""),   # no original clip
              ])
    pred = pd.Series([2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], index=range(1, 9))
    cache = tmp_path / "cache"
    new, log = P.apply_rules(pred, df, rules=("twin",), video_root=vids, cache_dir=cache)
    assert new[2] == 2.0                               # copied from qid 1 (whitespace in the question ignored)
    assert new[3] == 4.0 and new[5] == 6.0             # no matching original row (question / prior differ)
    assert new[7] == 8.0 and new[8] == 9.0             # rotated original: not copied
    skip = log[~log.applied].set_index("qid")
    assert "rotated" in skip.reason[7]
    applied = log[log.applied]
    assert list(applied.qid) == [2] and applied.source_qid.iloc[0] == 1 and applied.rule.iloc[0] == "twin"
    assert (cache / f"twins_v{P.CACHE_VERSION}.json").exists()
    # a re-run reads the verdicts from the cache, not the videos
    monkeypatch.setattr(P, "read_frames", lambda *a, **k: (_ for _ in ()).throw(AssertionError("re-read")))
    new2, _ = P.apply_rules(pred, df, rules=("twin",), video_root=vids, cache_dir=cache)
    assert new2.equals(new)
    # without frames nothing can be verified: no copy
    new3, log3 = P.apply_rules(pred, df, rules=("twin",), use_frames=False)
    assert new3.equals(pred) and set(log3.reason) == {"skipped: twin frames missing"}


def test_twin_copies_final_value_and_keeps_own_fact(aligned_twins):
    depth = "t=0s, distance_boat_camera = 12.345m\nt=1s, distance_boat_camera = 13.456m"
    df = _df([(1, "simulation_0001", "What is the length of the boat in meters?", "speed of the boat = 4m/s", depth),
              (2, "simulation_0001", "What is the height of the boat in meters?", "speed of the boat = 4m/s", depth),
              (3, "simulation_0001_segmented", "What is the length of the boat in meters?", "speed of the boat = 4m/s",
               depth),
              (4, "simulation_0001_segmented", "What is the height of the boat in meters?", "speed of the boat = 4m/s",
               depth),
              (5, "simulation_0002", "What is the speed of the eagle in m/s?", "height of the boat = 9.5m", depth),
              ])
    pred = pd.Series([11.0, 8.0, 12.0, 7.0, 3.0], index=range(1, 6))
    new, log = P.apply_rules(pred, df, use_frames=True, cache_dir=None)
    assert new[2] == 9.5 and new[4] == 9.5            # the stated height (same family by depth_info numbers)
    assert new[3] == 11.0                             # twin follows the original's final answer
    assert set(log[log.applied].rule) == {"facts", "twin"}
    assert "own stated fact" in log[(log.qid == 4) & (log.rule == "twin")].reason.iloc[0]


# ----------------------------------------------------------------------------- render rule

def test_render_rule_motion_only_and_mask():
    pr, d = "diameter of the ball = 6.7cm", "distance_ball_camera = 1.401m"
    sp = "What is the speed of the ball at 1.0s in cm/s?"
    df = _df([(1, "captured_0005", sp, pr, d, "D3"),
              (2, "captured_0005s", sp, pr, d, "D3"),
              (3, "captured_0005x", sp.replace("1.0s", "1s"), pr, d, "D3"),
              (4, "captured_0005", "What is the height of the table in cm?", pr, d, "S3"),
              (5, "captured_0005s", "What is the height of the table in cm?", pr, d, "S3"),
              (6, "captured_0005s", sp, pr, "distance_ball_camera = 1.5m", "D3"),       # other depth_info
              (7, "captured_0006s", sp, pr, d, "D3"),                                 # no base render
              (8, "captured_0005s", "What is the distance travelled by the ball from 0s to 2s in cm?", pr, d, "S3"),
              (9, "captured_0005", "What is the distance travelled by the ball from 0s to 2s in cm?", pr, d, "S3"),
              ])
    pred = pd.Series([100.0, 150.0, 160.0, 70.0, 75.0, 140.0, 130.0, 50.0, 40.0], index=range(1, 10))
    new, log = P.apply_rules(pred, df, rules=("render",), use_frames=False)
    assert new[2] == 100.0 and new[3] == 100.0 and new[8] == 40.0
    assert new[5] == 75.0 and new[6] == 140.0 and new[7] == 130.0
    assert set(log.qid) == {2, 3, 8} and log.applied.all()
    mask = pd.Series({2: True, 3: False, 8: False})
    new, _ = P.apply_rules(pred, df, rules=("render",), use_frames=False, render_mask=mask)
    assert new[2] == 100.0 and new[3] == 160.0 and new[8] == 50.0
    # a missing / unusable base answer is never copied
    new, _ = P.apply_rules(pred.drop(1), df, rules=("render",), use_frames=False)
    assert new[2] == 150.0 and 1 not in new.index


# ----------------------------------------------------------------------------- facts rule

DEPTH_A = "distance_boat_camera = 12.345m\ndistance_pier_camera = 20.123m"


def test_facts_sizes_family_units_dimension_and_names():
    df = _df([(1, "simulation_0001", "What is the height of the man in meters?", "length of the boat = 10m", DEPTH_A),
              (2, "simulation_0002", "What is the length of the boat in cm?", "height of the person = 1.75m",
               DEPTH_A + "\ndistance_tree_camera = 30.5m"),
              (3, "simulation_0002", "What is the width of the boat in meters?", "height of the person = 1.75m", DEPTH_A),
              (4, "simulation_0002", "What is the diameter of the yellow car in meters?",
               "height of the person = 1.75m", DEPTH_A),
              (5, "simulation_0003", "What is the length of the boat in meters?",
               "diameter of the tire of the yellow car = 0.764m", DEPTH_A),
              (6, "simulation_0001", "What is the length of the boat in meters?", "length of the boat = 10m", DEPTH_A),
              (7, "simulation_0009", "What is the length of the boat in meters?", "height of the person = 1.8m",
               "distance_boat_camera = 99.999m"),
              (8, "simulation_0001", "What is the body length of the boat in meters?", "length of the boat = 10m",
               DEPTH_A),
              ])
    new, log = P.apply_rules(_pred(df), df, rules=("facts",), use_frames=False)
    assert new[1] == pytest.approx(1.75)              # man == person (qp.geometry synonyms)
    assert new[2] == pytest.approx(1000.0)            # 10 m stated, asked in cm
    assert new[3] == 1.0                              # width is not the stated length
    assert new[4] == 1.0                              # 'tire of the yellow car' is not the yellow car
    assert new[5] == pytest.approx(10.0)
    assert new[6] == 1.0                              # the question's own prior is not a transfer
    assert new[7] == 1.0                              # another scene (no shared depth numbers)
    assert new[8] == 1.0                              # same clip: its own prior line, again
    fam = P.scene_families(P._questions(df), P.scene_links(P._questions(df), P._parse_facts(P._questions(df))))
    assert fam["simulation_0001"] == fam["simulation_0003"] != fam["simulation_0009"]


def test_facts_links_by_prior_statement_and_lab_events():
    lab_depth = "distance_ball_camera = 1.401m\ndistance_cup_camera = 1.502m"
    df = _df([(1, "simulation_0011", "What is the length of the eagle in meters?", "speed of the bird = 6.25m/s", ""),
              (2, "simulation_0012", "What is the height of the tower in meters?", "speed of the bird = 6.25m/s", ""),
              (3, "simulation_0012", "What is the wingspan of the bird in meters?", "length of the eagle = 0.8m", ""),
              (4, "simulation_0013", "What is the length of the eagle in meters?", "speed of the bird = 6.3m/s", ""),
              (9, "captured_0001", "What is the height of the cup in cm?", "diameter of the ball = 6.7cm", lab_depth, "S3"),
              (10, "captured_0002", "What is the diameter of the ball in cm?", "height of the cup = 11cm", lab_depth,
               "S3"),
              (11, "captured_0001s", "What is the diameter of the ball in cm?", "height of the cup = 12cm", lab_depth,
               "S3"),
              ])
    new, log = P.apply_rules(_pred(df), df, rules=("facts",), use_frames=False)
    assert new[1] == pytest.approx(0.8)               # identical 3-digit prior statement links 0011 and 0012
    assert new[4] == 1.0                              # 6.3 (2 digits) is no evidence of the same scene
    # lab: sizes move only within one event (base clip + its s/x renders), never across events
    assert new[11] == pytest.approx(6.7) and new[9] == pytest.approx(12.0) and new[10] == 1.0
    q = P._questions(df)
    fam = P.scene_families(q, P.scene_links(q, P._parse_facts(q)))
    assert fam["captured_0001"] == fam["captured_0002"]  # identical depth numbers: one family, still no transfer


def test_facts_series_size_transfer():
    df = _df([(1, "simulation_0021", "What is the width of the house in meters?", "length of the car = 4m", ""),
              (2, "simulation_0021", "What is the height of the house in meters?", "length of the car = 4m", ""),
              (3, "simulation_0022", "What is the width of the house in meters?", "length of the car = 4m", ""),
              (4, "simulation_0022", "What is the height of the house in meters?", "length of the car = 4m", ""),
              (5, "simulation_0022", "What is the speed of the dog in m/s?", "height of the house = 7.5m", ""),
              ])
    new, log = P.apply_rules(_pred(df), df, rules=("facts",), use_frames=False)
    assert new[2] == pytest.approx(7.5)               # series link (identical prior text, 2 shared questions)
    assert new[4] == pytest.approx(7.5)               # same clip, another question's prior
    assert new[1] == 1.0 and new[3] == 1.0


def test_facts_motion_time_acceleration_guard_conflict_and_tiers():
    track = "t=0s, distance_car_camera = 10.111m\nt=1s, distance_car_camera = 12.222m"
    other = "distance_tree_camera = 30.555m\ndistance_road_camera = 8.444m"
    df = _df([(1, "simulation_0031", "What is the height of the tree in meters?", "speed of the car = 5m/s",
               track + "\n" + other, "D3"),
              (2, "simulation_0032", "What is the speed of the car at 1.0s in m/s?", "height of the tree = 6m",
               track + "\n" + other, "D3"),
              (3, "simulation_0032", "What is the speed of the car from 1s to 2s in m/s?", "height of the tree = 6m",
               track + "\n" + other, "D3"),
              (4, "simulation_0033", "What is the speed of the car at 1.0s in m/s?", "height of the tree = 6m",
               other, "D3"),                                         # family only (shared tree/road numbers)
              (5, "simulation_0034", "What is the speed of the car at 1.0s in m/s?", "speed of the car = 5.5m/s",
               "distance_x_camera = 1.234m\n" + other, "D3"),      # a second, different stated car speed
              (6, "simulation_0035", "What is the speed of the truck at 1.0s in m/s?", "gravity = 9.8m/s^2",
               other, "D3"),
              (7, "simulation_0036", "What is the speed of the truck at 2.0s in m/s?", "speed of the truck at 2s = 3m/s",
               other, "D3"),
              (8, "simulation_0037", "What is the speed of the trolley at 1.0s in m/s?",
               "acceleration of the trolley = 1.5m/s", other, "D3"),
              (9, "simulation_0038", "What is the speed of the trolley at 1.0s in m/s?", "height of the tree = 6m",
               other, "D3"),
              (10, "simulation_0039", "What is the speed of the bus at 1.0s in m/s?", "speed of the bus = 9m/s",
               other, "D3"),
              (11, "simulation_0040", "What is the speed of the bus at 1.0s in m/s?", "height of the tree = 6m",
               other, "D3"),
              (12, "simulation_0040", "What is the acceleration of the bus at 1.0s in m/s^2?", "height of the tree = 6m",
               other, "D3"),
              ])
    pred = _pred(df, 4.0)
    new, log = P.apply_rules(pred, df, rules=("facts",), use_frames=False)
    L = log.set_index("qid")
    # tier 1 (identical depth track of the car with 0031) wins over the family's conflicting 5.5
    assert new[2] == pytest.approx(5.0) and "identical depth track" in L.reason[2]
    assert new[3] == pytest.approx(5.0)              # an untimed (constant) speed also answers a window
    # only family links: 5 and 5.5 are both stated -> conflict, unchanged
    assert new[4] == 4.0 and not L.applied[4] and "conflicting" in L.reason[4]
    assert new[6] == 4.0                              # 'speed of the truck at 2s' does not answer t=1s
    assert new[9] == 4.0                              # 'acceleration ... = 1.5m/s' is an acceleration (unit typo)
    assert new[11] == 4.0                             # the bus accelerates in 0040: a constant speed does not apply
    # the speed guard: a stated speed far from the clip's own answer is reported, not applied
    pred2 = pred.copy()
    pred2[2] = 0.5
    new2, log2 = P.apply_rules(pred2, df, rules=("facts",), use_frames=False)
    assert new2[2] == 0.5 and "off the clip's own answer" in log2.set_index("qid").reason[2]
    new3, _ = P.apply_rules(pred2, df, rules=("facts",), use_frames=False, speed_guard=0)
    assert new3[2] == pytest.approx(5.0)


def test_facts_stated_at_the_asked_time():
    other = "distance_tree_camera = 30.555m\ndistance_road_camera = 8.444m"
    df = _df([(1, "simulation_0036", "What is the height of the tree in meters?", "speed of the truck at 2s = 3m/s",
               other, "D3"),
              (2, "simulation_0035", "What is the speed of the truck at 2.0s in m/s?", "height of the tree = 6m",
               other, "D3"),
              (3, "simulation_0035", "What is the speed of the truck at 1.0s in m/s?", "height of the tree = 6m",
               other, "D3"),
              (4, "simulation_0035", "What is the acceleration of the ball in m/s^2?", "gravity acceleration = 9.8m/s^2",
               other, "D3"),
              (5, "simulation_0036", "What is the acceleration of the ball in m/s^2?", "height of the tree = 6m",
               other, "D3"),
              ])
    new, _ = P.apply_rules(_pred(df, 2.5), df, rules=("facts",), use_frames=False)
    assert new[2] == pytest.approx(3.0) and new[3] == 2.5
    assert new[5] == 2.5                               # gravity priors are not stated facts


def test_answers_are_never_read_and_bad_rules_rejected():
    df = _df([(1, "captured_0005", "What is the speed of the ball at 1.0s in cm/s?", "p = 1cm", "d", "D3"),
              (2, "captured_0005s", "What is the speed of the ball at 1.0s in cm/s?", "p = 1cm", "d", "D3")])
    pred = pd.Series([10.0, 20.0], index=[1, 2])
    a, la = P.apply_rules(pred, df, use_frames=False)
    b, lb = P.apply_rules(pred, df.assign(answer=[123.0, 456.0], ground_truth_posterior=[7.0, 8.0]),
                          use_frames=False)
    assert a.equals(b) and la.equals(lb) and not ({123.0, 456.0, 7.0, 8.0} & set(b))
    with pytest.raises(ValueError):
        P.apply_rules(pred, df, rules=("twin", "pooling"))


def test_summary_counts():
    log = pd.DataFrame([dict(qid=1, rule="twin", old=1.0, new=2.0, applied=True),
                        dict(qid=2, rule="twin", old=1.0, new=1.0, applied=True),
                        dict(qid=3, rule="facts", old=1.0, new=math.nan, applied=False)])
    s = P.summary(log).set_index("rule")
    assert s.loc["twin", "applied"] == 2 and s.loc["twin", "changed"] == 1 and s.loc["facts", "skipped"] == 1


# ----------------------------------------------------------------------------- CLI

def _script():
    spec = importlib.util.spec_from_file_location("pp_script", ROOT / "scripts" / "postprocess.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cli_writes_id_parsed_value_and_log(tmp_path):
    rows = pd.DataFrame({
        "Unnamed: 0": [1, 2, 3],
        "video_id": ["captured_0005", "captured_0005s", "simulation_0001"],
        "video_type": ["V3LS", "V3LS", "V2SS"], "fps": [24, 24, 24], "inference_type": ["DD", "DD", "SS"],
        "question": ["What is the speed of the ball at 1.0s in cm/s?"] * 2 + ["What is the width of the box in m?"],
        "ground_truth_prior": ["diameter of the ball = 6.7cm"] * 2 + ["length of the box = 2m"],
        "depth_info": ["distance_ball_camera = 1.401m"] * 2 + [""],
        "video_source": ["lab", "lab", "simulation"], "ground_truth_posterior": [99.0, 98.0, 97.0]})
    qcsv = tmp_path / "q.csv"
    rows.rename(columns={"Unnamed: 0": ""}).to_csv(qcsv, index=False)
    pred = tmp_path / "pred.csv"
    pd.DataFrame({"id": [1, 2, 3], "parsed_value": [100.0, 150.0, 2.0], "method": ["geometry", "direct", "direct"]}
                 ).to_csv(pred, index=False)
    out, log = tmp_path / "out.csv", tmp_path / "log.csv"
    m = _script()
    assert m.main([str(pred), str(out), "--csv", str(qcsv), "--no-frames", "--log", str(log)]) == 0
    o = pd.read_csv(out)
    assert list(o.columns) == ["id", "parsed_value"] and o.parsed_value.tolist() == [100.0, 100.0, 2.0]
    lg = pd.read_csv(log)
    assert list(lg.columns) == P.LOG_COLUMNS and lg.qid.tolist() == [2]
    # render restricted to direct-routed rows; rule selection
    assert m.main([str(pred), str(out), "--csv", str(qcsv), "--no-frames", "--render-direct-only"]) == 0
    assert pd.read_csv(out).parsed_value.tolist() == [100.0, 100.0, 2.0]
    assert m.main([str(pred), str(out), "--csv", str(qcsv), "--no-frames", "--rules", "twin", "facts"]) == 0
    assert pd.read_csv(out).parsed_value.tolist() == [100.0, 150.0, 2.0]
    pd.DataFrame({"id": [1, 2, 3], "parsed_value": [100.0, 150.0, 2.0]}).to_csv(pred, index=False)
    with pytest.raises(SystemExit):
        m.main([str(pred), str(out), "--csv", str(qcsv), "--no-frames", "--render-direct-only"])


# ----------------------------------------------------------------------------- real test set

def _have_test_data() -> bool:
    from qp.data import TEMPLATE_CSV, TEST_DIR
    return TEMPLATE_CSV.exists() and any(TEST_DIR.glob("*.parquet")) and any(TEST_DIR.glob("*.mp4"))


real = pytest.mark.skipif(not _have_test_data(), reason="needs data/QuantiPhy (test videos + parquet) and the template")


@pytest.fixture(scope="module")
def real_run():
    from qp.data import load_split
    t = load_split("test")
    pred = pd.Series(1.0 + t.qid.to_numpy() / 1e4, index=t.qid.astype(int))     # distinct, model-free values
    new, log = P.apply_rules(pred, t, speed_guard=0)
    return t, pred, new, log


@real
def test_real_twins_rotated_views_excluded(real_run):
    t, pred, new, log = real_run
    T = t.set_index("qid")
    tw = log[log.rule == "twin"]
    rot = tw[tw.reason.str.contains("rotated", na=False)]
    assert set(rot.qid.map(T.video_id)) == {"simulation_0017_segmented", "simulation_0019_segmented"}
    assert all(new[q] == pred[q] for q in rot.qid)
    ok = tw[tw.applied]
    assert len(ok) >= 200 and not tw.reason.str.contains("missing|unknown", na=False).any()
    for r in ok.itertuples():                          # every copy comes from the original clip, same question
        s, o = T.loc[r.qid], T.loc[int(r.source_qid)]
        assert o.video_id == P.twin_original(s.video_id) and P.norm_question(o.question) == P.norm_question(s.question)
        assert P.exact_text(o.prior) == P.exact_text(s.prior) and new[r.qid] == new[int(r.source_qid)]


@real
def test_real_render_and_facts(real_run):
    t, pred, new, log = real_run
    T = t.set_index("qid")
    rd = log[(log.rule == "render") & log.applied]
    assert len(rd) >= 200
    assert set(rd.qid.map(T.video_id).map(P.lab_base)) == set(rd.source_clip)
    assert set(rd.qid.map(T.category)) <= {"D2", "S3", "D3"}
    f = log[(log.rule == "facts") & log.applied].set_index("qid")
    assert len(f) >= 100
    expect = {11: 10.0, 13: 4.0, 34: 5.44, 1103: 10.0, 1109: 11.84, 1134: 1.87, 1147: 12.0, 1497: 5.0, 1468: 5.0,
              1452: 2.47, 1242: 5.33}
    for q, v in expect.items():
        assert new[q] == pytest.approx(v), q
    skipped = log[(log.rule == "facts") & ~log.applied].set_index("qid")
    assert "conflicting" in skipped.reason[1129]       # eagle 11.84 (footage B) vs 12 (footage C), family links only


@real
def test_real_agreement_with_probe5_when_available():
    v3p = ROOT / "submissions" / "trackA_v3_best_per_category.csv"
    p5p = ROOT / "submissions" / "trackA_probe5_families_merged.csv"
    if not (v3p.exists() and p5p.exists()):
        pytest.skip("submissions/ CSVs not present")
    from qp.data import load_split
    t = load_split("test")
    T = t.set_index("qid")
    v3 = pd.read_csv(v3p).set_index("id").parsed_value
    p5 = pd.read_csv(p5p).set_index("id").parsed_value
    new, log = P.apply_rules(v3, t)
    L = log[log.applied & ~np.isclose(log.new, log.old, rtol=1e-9)].copy()
    L["cat"] = L.qid.map(T.category)
    L["same"] = np.isclose(L.new, L.qid.map(p5), rtol=1e-6)
    for rule, cat in (("twin", "S2"), ("twin", "S3"), ("render", "S3")):
        x = L[(L.rule == rule) & (L.cat == cat)]
        assert len(x) > 30 and x.same.all(), (rule, cat)
    f = L[(L.rule == "facts") & L.cat.isin(["S2", "S3", "D3"])]
    assert f.same.mean() > 0.9
