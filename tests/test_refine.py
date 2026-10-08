import math

import cv2
import numpy as np
import pytest

from qp import refine
from qp.claude_annotate import Annotation
from qp.spec import Obs, Quantity, QuestionSpec, RoleTrack

FPS, W, H = 25.0, 320, 240


def _video(path, n=50, vx=0.7, pan=0.0):
    """A soft grey disc drifting vx px/frame over a static textured background (pan > 0: the
    whole scene shifts, i.e. a moving camera)."""
    rng = np.random.default_rng(0)
    bg = cv2.GaussianBlur(rng.random((H, W)), (0, 0), 2)
    bg = cv2.normalize(bg, None, 20, 200, cv2.NORM_MINMAX).astype(np.uint8)   # contrasted texture
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for i in range(n):
        img = np.roll(bg, int(round(pan * i)), axis=1).copy()
        cv2.circle(img, (int(round((80 + vx * i) * 16)), 120 * 16), 9 * 16, 250, -1, lineType=cv2.LINE_AA,
                   shift=4)  # sub-pixel centre
        img = cv2.GaussianBlur(img, (0, 0), 1.0)
        vw.write(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR))
    vw.release()
    return str(path)


def _ann(points):
    spec = QuestionSpec(qid=1, target=Quantity("size", ["drop"]), prior=Quantity("speed", ["disc"], value_si=1.0))
    obs = [Obs(t=f / FPS, point=list(p), box=[p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9]) for f, p in points]
    return Annotation(spec=spec, tracks=[RoleTrack("prior", "disc", obs), RoleTrack("target", "drop", list(obs))],
                      direct_answer=None, confidence=None)


def test_refines_a_slow_prior_track_read_inconsistently(tmp_path):
    path = _video(tmp_path / "v.mp4")
    # true motion 0.7 px/frame (34 px over 49 frames); the annotator's points wander and read 20 px
    a = _ann([(0, (78.0, 121.0)), (16, (88.0, 119.0)), (33, (95.0, 121.0)), (49, (98.0, 120.0))])
    log = []
    refine.refine_annotations({1: a}, {1: path}, {1: (FPS, (W, H))}, log=log)
    assert "prior_track_refined" in a.flags, log
    pts = [o for o in a.tracks[0].obs if o.point is not None]
    assert len(pts) == 50 and pts[0].t == 0 and pts[-1].t == pytest.approx(49 / FPS)
    moved = pts[-1].point[0] - pts[0].point[0]
    assert moved == pytest.approx(0.7 * 49, abs=2.0)
    assert sum(o.box is not None for o in a.tracks[0].obs) == 4                 # boxes kept
    assert len(a.tracks[1].obs) == 4 and a.tracks[1].obs[0].point == [78.0, 121.0]  # targets untouched


def test_guards_keep_the_annotators_track(tmp_path):
    pan = _video(tmp_path / "pan.mp4", pan=3.0)
    a = _ann([(0, (78.0, 121.0)), (49, (112.0, 120.0))])
    log = []
    refine.refine_annotations({1: a}, {1: pan}, {1: (FPS, (W, H))}, log=log)
    assert "prior_track_refined" not in a.flags and log[0][2]["why"] == "camera_not_static"
    still = _video(tmp_path / "v.mp4")
    b = _ann([(0, (78.0, 121.0)), (49, (40.0, 120.0))])                          # wrong direction
    log = []
    refine.refine_annotations({1: b}, {1: still}, {1: (FPS, (W, H))}, log=log)
    assert "prior_track_refined" not in b.flags and log[0][2]["why"] in ("direction", "deviation")
    c = _ann([(0, (78.0, 121.0))])                                               # one point: nothing to do
    refine.refine_annotations({1: c}, {1: still}, {1: (FPS, (W, H))})
    assert len(c.tracks[0].obs) == 1
    d = _ann([(0, (78.0, 121.0)), (49, (112.0, 120.0))])
    d.spec.prior = Quantity("size", ["disc"], value_si=0.1)                     # a size prior is not refined
    refine.refine_annotations({1: d}, {1: still}, {1: (FPS, (W, H))})
    assert len(d.tracks[0].obs) == 2 and not math.isnan(d.tracks[0].obs[1].point[0])


def test_an_unexpected_error_keeps_the_tracks_and_flags(tmp_path, monkeypatch):
    path = _video(tmp_path / "v.mp4")
    a = _ann([(0, (78.0, 121.0)), (16, (88.0, 119.0)), (49, (98.0, 120.0))])
    before = [o.point for o in a.tracks[0].obs]

    def boom(*args, **kwargs):
        raise MemoryError("decode")
    monkeypatch.setattr(refine.VideoFlow, "track_many", boom)
    log = []
    refine.refine_annotations({1: a}, {1: path}, {1: (FPS, (W, H))}, log=log)   # does not raise
    assert "prior_refine_error" in a.flags and "prior_track_refined" not in a.flags
    assert [o.point for o in a.tracks[0].obs] == before and log[0][2]["why"] == "error:MemoryError"


def test_full_resolution_copy_is_refined_at_the_480p_scale(tmp_path):
    """A 4x copy of the scene (1280x960) is tracked on frames downscaled to a 480 px short side (the
    pixel thresholds are 480p pixels): the path comes back in original pixels, 4x the 320x240 motion."""
    k, n, vx = 4, 50, 0.7
    rng = np.random.default_rng(0)
    bg = cv2.GaussianBlur(rng.random((H, W)), (0, 0), 2)
    bg = cv2.resize(cv2.normalize(bg, None, 20, 200, cv2.NORM_MINMAX), (W * k, H * k), interpolation=cv2.INTER_CUBIC)
    bg = np.clip(bg, 0, 255).astype(np.uint8)
    path = str(tmp_path / "big.mp4")
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W * k, H * k))
    for i in range(n):
        img = bg.copy()
        cv2.circle(img, (int(round((80 + vx * i) * k * 16)), 120 * k * 16), 9 * k * 16, 250, -1,
                   lineType=cv2.LINE_AA, shift=4)
        vw.write(cv2.cvtColor(cv2.GaussianBlur(img, (0, 0), k), cv2.COLOR_GRAY2BGR))
    vw.release()
    flow = refine.VideoFlow(path)
    assert flow.scale == pytest.approx(0.5) and flow.work_size == (640, 480)
    pts = [(0, (78.0, 121.0)), (16, (88.0, 119.0)), (33, (95.0, 121.0)), (49, (98.0, 120.0))]
    a = _ann([(f, (x * k, y * k)) for f, (x, y) in pts])
    for o in a.tracks[0].obs:
        o.box = [o.point[0] - 9 * k, o.point[1] - 9 * k, o.point[0] + 9 * k, o.point[1] + 9 * k]
    log = []
    refine.refine_annotations({1: a}, {1: path}, {1: (FPS, (W * k, H * k))}, log=log)
    assert "prior_track_refined" in a.flags, log
    assert log[0][2]["work_scale"] == pytest.approx(0.5)
    dense = [o for o in a.tracks[0].obs if o.point is not None]
    assert len(dense) == n and dense[0].point == pytest.approx([78.0 * k, 121.0 * k], abs=1e-6)
    assert dense[-1].point[0] - dense[0].point[0] == pytest.approx(vx * (n - 1) * k, abs=2.0 * k)
