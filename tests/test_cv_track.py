import importlib.util
import io
import json
import math
import re
import subprocess
import sys
import types
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest

from qp.geometry import solve
from qp.open import cv_track as cv
from qp.spec import Quantity, QuestionSpec, RoleTrack
from synth import Body, Camera, ballistic, render_video, static

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "colab_pipeline.ipynb"
W, H = 854, 480


def rect_mask(x0, y0, x1, y1, shape=(H, W)):
    m = np.zeros(shape, bool)
    m[y0:y1, x0:x1] = True
    return m


def disc_mask(cx, cy, r, shape=(H, W)):
    yy, xx = np.mgrid[:shape[0], :shape[1]]
    return (xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2 <= r * r


def ellipse_mask(cx, cy, a, b, angle_deg=0.0, shape=(H, W)):
    """Pixels whose centre is inside the ellipse with semi-axes a (along angle) and b."""
    yy, xx = np.mgrid[:shape[0], :shape[1]]
    th = math.radians(angle_deg)
    u, v = xx + 0.5 - cx, yy + 0.5 - cy
    p, q = u * math.cos(th) + v * math.sin(th), -u * math.sin(th) + v * math.cos(th)
    return (p / a) ** 2 + (q / b) ** 2 <= 1


def length(ext):
    return math.dist(*ext)


# ---------------------------------------------------------------- mask -> measurements

def test_axis_aligned_rectangle():
    f = cv.mask_features(rect_mask(200, 100, 300, 150))
    assert f["box"] == [200, 100, 300, 150] and f["area"] == 5000 and not f["edge"]
    assert f["c"] == [250.0, 125.0]
    assert cv.extent_from_features(f, "vertical") == [[250.0, 100.0], [250.0, 150.0]]
    assert cv.extent_from_features(f, "horizontal") == [[200.0, 125.0], [300.0, 125.0]]
    assert length(cv.extent_from_features(f, "major")) == pytest.approx(100.0)
    assert length(cv.extent_from_features(f, "minor")) == pytest.approx(50.0)
    assert cv.point_from_features(f) == [250.0, 125.0]
    assert cv.point_from_features(f, "bottom") == [250.0, 150.0]


@pytest.mark.parametrize("angle", [0.0, 17.0, 30.0, 45.0, 72.0, 120.0])
def test_rotated_rectangle_axes(angle):
    yy, xx = np.mgrid[:H, :W]
    th = math.radians(angle)
    u, v = xx + 0.5 - 400.0, yy + 0.5 - 240.0      # pixels whose centre lies inside the rectangle
    p, q = u * math.cos(th) + v * math.sin(th), -u * math.sin(th) + v * math.cos(th)
    f = cv.mask_features((np.abs(p) <= 80.0) & (np.abs(q) <= 20.0))
    major, minor = cv.extent_from_features(f, "major"), cv.extent_from_features(f, "minor")
    assert length(major) == pytest.approx(160.0, abs=1.5)    # pixel squares: exact when axis-aligned
    assert length(minor) == pytest.approx(40.0, abs=1.5)
    d = (np.subtract(major[1], major[0]))
    ang = math.degrees(math.atan2(d[1], d[0])) % 180
    assert min(abs(ang - angle % 180), 180 - abs(ang - angle % 180)) < 1.5
    mid = np.mean(major, axis=0)
    assert np.allclose(mid, [400.0, 240.0], atol=1.0)
    # height of a rotated object = its vertical span, through the centroid
    vert = cv.extent_from_features(f, "vertical")
    assert length(vert) == f["box"][3] - f["box"][1] and vert[0][0] == f["c"][0]


@pytest.mark.parametrize("r", [6.0, 12.5, 30.0])
def test_circle_diameter_and_radius(r):
    f = cv.mask_features(disc_mask(300.0, 200.0, r))
    for name in ("ball", "cookie", "object"):
        assert length(cv.extent_from_features(f, "diameter", name)) == pytest.approx(2 * r, rel=0.03)
    assert length(cv.extent_from_features(f, "radius", "ball")) == pytest.approx(r, rel=0.03)
    assert np.allclose(np.mean(cv.extent_from_features(f, "diameter"), axis=0), [300.0, 200.0], atol=0.6)


def test_elongated_diameter_depends_on_object():
    # ellipse 2a=80 x 2b=40: a disc seen obliquely (wheel) -> major; a blurred ball or a tube -> minor
    f = cv.mask_features(ellipse_mask(400.0, 240.0, 40.0, 20.0, angle_deg=25.0))
    assert length(cv.extent_from_features(f, "diameter", "bicycle wheel")) == pytest.approx(80.0, abs=2.0)
    assert length(cv.extent_from_features(f, "diameter", "tennis ball")) == pytest.approx(40.0, abs=2.0)
    assert length(cv.extent_from_features(f, "diameter", "plunge tube")) == pytest.approx(40.0, abs=2.0)


def test_near_square_side_view_is_not_a_disc():
    # a cup / can seen from the side: 80 wide x 95 tall, fills its rectangle -> its width, not the
    # equal-area circle (98 px); a slightly elliptical disc (fill pi/4) still uses the circle
    f = cv.mask_features(rect_mask(300, 200, 380, 295))
    for name in ("cup", "trash can", "glass", "bottle"):
        assert length(cv.extent_from_features(f, "diameter", name)) == pytest.approx(80.0), name
    assert length(cv.extent_from_features(f, "diameter", "lid")) == pytest.approx(95.0)
    e = cv.mask_features(ellipse_mask(400.0, 240.0, 22.0, 20.0))
    assert length(cv.extent_from_features(e, "diameter", "cup")) == pytest.approx(2 * math.sqrt(22 * 20), rel=0.03)


def test_shape_words_need_word_boundaries():
    assert cv.is_sphere("basketball") and cv.is_sphere("yellow ballon") and cv.is_sphere("orange")
    assert cv.is_sphere("the orange on the table") and cv.is_sphere("model of Jupiter")
    assert not any(map(cv.is_sphere, ("orange car", "ballerina", "ballot box", "earthmover", "dropbox")))
    assert cv.dimension_mode("size", "orange car") == "major" and cv.dimension_mode("size", "ballerina") == "major"
    f = cv.mask_features(rect_mask(100, 200, 400, 300))      # elongated: a car's diameter is its long side
    assert length(cv.extent_from_features(f, "diameter", "orange car")) == pytest.approx(300.0)
    assert length(cv.extent_from_features(f, "diameter", "orange")) == pytest.approx(100.0)


def test_clean_mask_drops_small_blobs_and_edge_flag():
    m = rect_mask(100, 100, 140, 140)
    m[300:303, 600:603] = True           # 9 px speck, < 10% of the 1600 px object
    f = cv.mask_features(m)
    assert f["box"] == [100, 100, 140, 140] and f["area"] == 1600
    assert cv.mask_features(np.zeros((H, W), bool)) is None
    assert cv.mask_features(rect_mask(0, 50, 30, 80))["edge"]
    two = rect_mask(100, 100, 140, 140) | rect_mask(200, 100, 230, 140)   # occluded in two parts: both kept
    assert cv.mask_features(two)["box"] == [100, 100, 230, 140]


@pytest.mark.parametrize("dim,name,mode", [
    ("height", "", "vertical"), ("vertical height", "", "vertical"), ("height of the person", "", "vertical"),
    ("width", "", "horizontal"), ("shoulder breadth", "", "horizontal"), ("horizontal width", "", "horizontal"),
    ("thickness", "", "minor"), ("vertical depth (thickness)", "", "vertical"),
    ("length", "", "major"), ("wingspan", "", "major"), ("", "car", "major"), ("size", "ball", "diameter"),
    ("diameter", "", "diameter"), ("radius", "", "radius"), ("calibre", "", "diameter"),
    ("calibre", "bullet", "diameter"), ("length", "ruler", "major"), ("size", "basketball", "diameter"),
    # graduations of a measuring tool are no mask dimension (the whole ruler would be the "calibre")
    ("calibre", "ruler", None), ("graduation", "tape measure", None), ("", "smallest tick of the scale", None),
])
def test_dimension_mode(dim, name, mode):
    assert cv.dimension_mode(dim, name) == mode


def test_build_obs_drops_glitches_and_border_frames():
    frames = {}
    for k in range(20):
        x = 100 + 10 * k
        frames[str(k)] = {**cv.mask_features(rect_mask(x, 200, x + 40, 260)), "conf": 0.9}
    frames["7"] = {**cv.mask_features(rect_mask(150, 100, 400, 400)), "conf": 0.9}   # jumped to something big
    frames["19"] = {**cv.mask_features(rect_mask(W - 20, 200, W, 260)), "conf": 0.9}  # leaving the frame
    obs = cv.build_obs(frames, fps=10.0, extent_mode="major", name="box", det_score=0.5)
    assert [o.t for o in obs] == [k / 10 for k in range(20) if k != 7]
    last = obs[-1]
    assert last.point is None and last.extent is None and last.box == [W - 20.0, 200.0, float(W), 260.0]
    assert obs[0].point == [120.0, 230.0] and length(obs[0].extent) == pytest.approx(60.0)
    assert obs[0].score == pytest.approx(0.45)
    assert all(o.extent is None for o in cv.build_obs(frames, fps=10.0))


# ---------------------------------------------------------------- phrases and instances

@pytest.mark.parametrize("phrase,query,head,colors,spatial", [
    ("the woman in yellow", "woman", "woman", ["yellow"], []),
    ("light right above the woman's head", "light", "light", [], []),
    ("yellow ballon the left", "yellow ballon", "ballon", ["yellow"], ["left"]),
    ("bycicle on the upper left conrner", "bycicle", "bycicle", [], ["left", "top"]),
    ("white car in the roundabout", "white car", "car", ["white"], []),
    ("pedestal (square base) of the central sculpture", "pedestal of sculpture", "pedestal", [], ["center"]),
    ("person on the left (the passer)", "person", "person", [], ["left"]),
    ("person standing in the middle", "person", "person", [], ["center"]),
    ("model of Jupiter (the one at the center)", "model of jupiter", "model", [], ["center"]),
    ("big bird", "bird", "bird", [], ["large"]),
    ("purple ball", "purple ball", "ball", ["purple"], []),
    ("two black road signs", "black road signs", "sign", ["black"], []),
    ("car in front of the bus", "car", "car", [], []),
    ("balck ball", "balck ball", "ball", ["black"], []),      # typos in the official questions
    ("yelow car", "yelow car", "car", ["yellow"], []),
    ("back wheel", "wheel", "wheel", [], ["back"]),
    # participle clauses: the subject is the object, not the verb's object
    ("saw cutting the block", "saw", "saw", [], []),
    ("man riding the bicycle", "man", "man", [], []),
    ("woman holding an umbrella", "woman", "woman", [], []),
    ("red dog chasing the ball on the lawn", "red dog", "dog", ["red"], []),
    ("walking pedestrian", "walking pedestrian", "pedestrian", [], []),     # -ing words that are no clause
    ("turning yellow car", "turning yellow car", "car", ["yellow"], []),
    ("skynova lettering on the bottle", "skynova lettering", "lettering", [], []),
    ("ball return opening", "ball return opening", "opening", [], []),
    ("the building on the left", "building", "building", [], ["left"]),
])
def test_parse_phrase(phrase, query, head, colors, spatial):
    h = cv.parse_phrase(phrase)
    assert (h.query, h.head, h.colors, sorted(h.spatial)) == (query, head, colors, sorted(spatial))


def test_parse_phrase_ordinal_and_keys():
    h = cv.parse_phrase("second ball from the left")
    assert (h.query, h.spatial, h.ordinal) == ("ball", ["left"], 1)
    assert cv.object_key("Black car 2") == ("black car", 1)
    assert cv.object_key("ball #1") == ("ball", 0)
    assert cv.object_key("the piano 2") == ("piano", 1)
    assert cv.object_key("The person's bag") == ("person bag", None)
    P = cv.parse_phrase
    assert P("purple ball").distinct_from(P("black ball"))
    assert P("left tennis ball").distinct_from(P("right tennis ball"))
    assert P("second ball from the left").distinct_from(P("left ball"))
    assert not P("ball").distinct_from(P("ping pong ball"))
    assert not P("purple ball").distinct_from(P("purple car"))
    # a bare phrase may mean any instance; descriptors of different types do not conflict
    for a, b in (("tennis ball", "left tennis ball"), ("car", "white car"), ("purple ball", "left ball")):
        assert not P(a).distinct_from(P(b)) and not P(b).distinct_from(P(a)), (a, b)


def scene(colors_boxes, shape=(H, W), bg=(30, 120, 40)):
    img = np.zeros((*shape, 3), np.uint8)
    img[:] = bg
    for rgb, (x0, y0, x1, y1) in colors_boxes:
        img[y0:y1, x0:x1] = rgb
    return img


def cand(box, score=0.8, label="ball"):
    return {"box": [float(v) for v in box], "score": score, "label": label}


BOXES = [(100, 200, 140, 240), (400, 210, 440, 250), (700, 190, 740, 230)]


def test_choose_instance_by_colour():
    img = scene([((90, 30, 140), BOXES[0]), ((10, 10, 10), BOXES[1]), ((240, 240, 240), BOXES[2])])
    cands = [cand(b, s) for b, s in zip(BOXES, (0.9, 0.7, 0.6))]
    for phrase, want in (("purple ball", 0), ("black ball", 1), ("white ball", 2), ("ball", 0)):
        i, q, n = cv.choose_instance(cands, cv.parse_phrase(phrase), (W, H), img)
        assert i == want, phrase
    assert cv.color_fraction(img, BOXES[1], ["black"]) == pytest.approx(1.0)
    assert cv.color_fraction(img, BOXES[1], ["purple"]) == pytest.approx(0.0)


def test_choose_instance_spatial_size_ordinal():
    cands = [cand(BOXES[1], 0.9), cand(BOXES[0], 0.8), cand((300, 350, 420, 470), 0.85), cand(BOXES[2], 0.7)]
    pick = lambda p: cv.choose_instance(cands, cv.parse_phrase(p), (W, H))[0]  # noqa: E731
    assert pick("left ball") == 1 and pick("right ball") == 3 and pick("leftmost ball") == 1
    assert pick("ball at the top") == 3 and pick("bottom ball") == 2
    assert pick("big ball") == 2 and pick("small ball") in (0, 1, 3)
    assert pick("ball in the center") == 0 and pick("front ball") == 2
    assert pick("second ball from the left") == 2 and pick("third ball from the left") == 0
    assert pick("ball") == 0
    # weak spurious detections are not eligible for the spatial choice
    weak = cands + [cand((5, 5, 20, 20), 0.3)]
    assert cv.choose_instance(weak, cv.parse_phrase("left ball"), (W, H))[0] == 1


def test_choose_instance_pairs_taken_and_labels():
    cands = [cand(BOXES[2], 0.9), cand(BOXES[0], 0.85), cand(BOXES[1], 0.3)]
    h = cv.parse_phrase("ball")
    a, qa, _ = cv.choose_instance(cands, h, (W, H), rank=0)
    b, qb, _ = cv.choose_instance(cands, h, (W, H), rank=1)
    assert (a, b) == (1, 0) and qa == qb          # same pair, ordered left to right
    assert cv.choose_instance(cands[:1], h, (W, H), rank=1)[0] is None
    i, _, _ = cv.choose_instance(cands, h, (W, H), taken=[cands[0]["box"]])
    assert i == 1                                 # the best box is taken by another described object
    mixed = [cand(BOXES[0], 0.9, "sculpture"), cand(BOXES[1], 0.5, "pedestal")]
    assert cv.choose_instance(mixed, cv.parse_phrase("pedestal of the sculpture"), (W, H))[0] == 1


def test_pick_keyframe_prefers_complete_frames_and_interior_boxes():
    h = cv.parse_phrase("right ball")
    dets = {0: [cand(BOXES[0], 0.95)],                       # only one ball visible: ambiguous
            10: [cand(BOXES[0], 0.8), cand(BOXES[1], 0.8)]}
    f, i, _ = cv.pick_keyframe(dets, h, (W, H))
    assert (f, dets[f][i]["box"]) == (10, [float(v) for v in BOXES[1]])
    dets = {0: [cand((0, 100, 40, 140), 0.9)], 5: [cand(BOXES[0], 0.8)]}
    assert cv.pick_keyframe(dets, cv.parse_phrase("ball"), (W, H))[0] == 5
    assert cv.pick_keyframe({0: []}, h, (W, H)) is None


def test_nms_and_iou():
    a, b = [0, 0, 10, 10], [5, 0, 15, 10]
    assert cv.iou(a, b) == pytest.approx(50 / 150)
    kept = cv.nms([cand(a, 0.5), cand([0, 0, 10, 11], 0.9), cand([50, 50, 60, 60], 0.4)])
    assert [k["score"] for k in kept] == [0.9, 0.4]


# ---------------------------------------------------------------- specs -> objects

def Q(kind, objs, **kw):
    return Quantity(kind=kind, objects=list(objs), **kw)


def test_plan_objects():
    specs = {
        1: QuestionSpec(1, Q("distance", ["black car", "black car"], unit="m"), Q("speed", ["person"], value_si=1.2)),
        2: QuestionSpec(2, Q("size", ["black car"], dimension="length"), Q("speed", ["person"], value_si=1.2)),
        3: QuestionSpec(3, Q("speed", ["ball"], time=1.0), Q("acceleration", ["gravity"], value_si=9.8)),
        4: QuestionSpec(4, Q("camera_distance", ["ball"]), Q("speed", ["ball"], value_si=2.0)),
        5: QuestionSpec(5, Q("distance", ["car 1", "car 2"]), Q("size", ["lane"], dimension="width", value_si=3.6)),
    }
    objects, roles = cv.plan_objects(specs)
    assert [(r, k) for r, k, _ in roles[1]] == [("prior", "person"), ("target", "black car#0"),
                                                ("target2", "black car#1")]
    assert [(r, k) for r, k, _ in roles[2]] == [("prior", "person"), ("target", "black car")]
    assert [(r, k) for r, k, _ in roles[3]] == [("target", "ball")]
    assert [(r, k) for r, k, _ in roles[4]] == [("prior", "ball")]
    assert [(r, k) for r, k, _ in roles[5]] == [("prior", "lane"), ("target", "car#0"), ("target2", "car#1")]
    assert objects["black car#1"] == {"phrase": "black car", "rank": 1} and objects["person"]["rank"] is None
    assert set(objects) == {"person", "black car#0", "black car#1", "black car", "ball", "lane", "car#0", "car#1"}


def test_load_specs_formats(tmp_path):
    sp = QuestionSpec(11, Q("size", ["boat"], dimension="length", unit="m"),
                      Q("speed", ["boat"], value_si=1.5)).to_dict()
    d = tmp_path / "specs"
    d.mkdir()
    (d / "v1.json").write_text(json.dumps({"video_id": "v1", "questions": {"11": {"spec": sp, "flags": []}}}))
    claude = {"video_id": "v2", "parsed": {"questions": [{"qid": 12, "spec": {k: v for k, v in sp.items()
                                                                               if k not in ("qid", "is_3d")},
                                                          "tracks": [], "direct_answer": 1.0}]}}
    (d / "v2.json").write_text(json.dumps(claude))
    (d / "bad.json").write_text("{not json")
    got = cv.load_specs(d)
    assert sorted(got) == [11, 12] and got[12].target.objects == ["boat"] and got[11].prior.value_si == 1.5
    (tmp_path / "s.jsonl").write_text(json.dumps({**sp, "qid": 13}) + "\n")
    assert list(cv.load_specs(tmp_path / "s.jsonl")) == [13]
    (tmp_path / "s.json").write_text(json.dumps([{**sp, "qid": 14}]))
    assert list(cv.load_specs(tmp_path / "s.json")) == [14]


def test_load_specs_parses_depth_text_for_old_claude_records(tmp_path):
    # a run_claude record made before meta stored depth_info: the questions' texts fill it in
    sp = QuestionSpec(12, Q("size", ["boat"], dimension="length", unit="m"), Q("size", ["mast"], value_si=3.0))
    body = {k: v for k, v in sp.to_dict().items() if k not in ("qid", "is_3d")}
    meta = {"video_id": "v2", "fps": 10.0, "video_type": "V3SC", "n_frames_total": 30, "scale": 1.0,
            "image_size": [640, 480], "frames": [0], "questions": [{"qid": 12, "target_unit": "m",
                                                                    "prior": "height of the mast = 3m"}]}
    rec = {"video_id": "v2", "status": "ok", "meta": meta,
           "parsed": {"questions": [{"qid": 12, "spec": body, "tracks": [], "direct_answer": 1.0}]}}
    (tmp_path / "v2.json").write_text(json.dumps(rec))
    assert cv.load_specs(tmp_path)[12].depth == []
    got = cv.load_specs(tmp_path, depth_texts={12: "distance_boat_camera = 4.5m"})[12]
    assert [(e.object, e.distance_m) for e in got.depth] == [("boat", 4.5)]


# ---------------------------------------------------------------- end to end with fake models

CAM = Camera()
FPS = 24.0
Z = 10.0
R_PX = 20                                        # render_video draws radius round(f size / 2Z) = 20 ...
SIZE = (2 * R_PX + 2) * Z / CAM.f                # ... and cv2.circle(LINE_AA) covers ~2r + 2 px: true size
RED = Body("red ball", ballistic([-3.0, 0.5, Z], [1.2, 0.0, 0.0]), size=2 * R_PX * Z / CAM.f, color=(0, 0, 255))
BLUE = Body("blue ball", static([2.0, -1.0, Z]), size=2 * R_PX * Z / CAM.f, color=(255, 0, 0))
COLOR_RGB = {"red": (255, 0, 0), "blue": (0, 0, 255)}


def _colour_mask(img, rgb):
    return (np.abs(img.astype(int) - np.array(rgb)).sum(axis=2) < 200)


class FakeDetector:
    """Colour-keyed 'detector': every disc is a 'ball'; colour words only change the label."""
    name = "fake"

    def __init__(self):
        self.calls = 0

    def detect(self, images, query):
        self.calls += 1
        out = []
        for img in images:
            cands = []
            for rgb in COLOR_RGB.values():
                f = cv.mask_features(_colour_mask(img, rgb))
                if f:
                    cands.append({"box": [float(v) for v in f["box"]], "score": 0.8, "label": "ball"})
            out.append(cands)
        return out


class FakeSegmenter:
    """'SAM 2': the colour under the prompt box centre, thresholded on every frame."""
    name = "fake-sam"

    def __init__(self):
        self.calls = 0

    def propagate(self, frames, prompts):
        self.calls += 1
        for oid, (k, box) in prompts.items():
            cx, cy = int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)
            rgb = frames[k][cy, cx].astype(int)
            for p, img in enumerate(frames):
                yield p, oid, _colour_mask(img, rgb), 0.95


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    d = tmp_path_factory.mktemp("cv")
    path = d / "synth_0001.mp4"
    render_video(str(path), [RED, BLUE], CAM, duration=2.0, fps=FPS)
    return path


def rows_for(video, qids):
    return pd.DataFrame({"qid": qids, "video_id": video.stem, "video_path": str(video), "fps": FPS,
                         "video_type": "S2MC"})


SPECS = {
    1: QuestionSpec(1, Q("speed", ["red ball"], time=1.0, unit="m/s"),
                    Q("size", ["blue ball"], dimension="diameter", value_si=SIZE)),
    2: QuestionSpec(2, Q("size", ["red ball"], dimension="diameter", unit="cm"),
                    Q("size", ["blue ball"], dimension="diameter", value_si=SIZE)),
    3: QuestionSpec(3, Q("distance", ["red ball", "blue ball"], time=0.0, unit="m"),
                    Q("size", ["blue ball"], dimension="diameter", value_si=SIZE)),
}


def test_track_video_end_to_end(video):
    det, seg = FakeDetector(), FakeSegmenter()
    trk = cv.CVTracker(det, seg, max_frames=360)
    rec, cache = trk.track_video(rows_for(video, [1, 2, 3]), SPECS)
    assert rec["meta"]["image_size"] == [CAM.width, CAM.height] and rec["meta"]["fps"] == FPS
    assert set(rec["objects"]) == {"red ball", "blue ball"}
    assert rec["objects"]["red ball"]["agree"] == 1.0 and rec["objects"]["blue ball"]["n_frames"] == 48
    json.dumps(cache)                                       # cache is JSON-able
    tr = {q: [RoleTrack.from_dict(t) for t in ts] for q, ts in rec["tracks"].items()}
    assert {t.role for t in tr["1"]} == {"prior", "target"} and tr["1"][0].source == "fake+sam2"
    ans = {q: solve(SPECS[int(q)], tr[q], (CAM.width, CAM.height), FPS) for q in tr}
    assert ans["1"].value == pytest.approx(1.2, rel=0.015)
    assert ans["2"].value == pytest.approx(SIZE * 100, rel=0.015)
    d0 = np.linalg.norm(RED.pos(0.0)[:2] - BLUE.pos(0.0)[:2])
    assert ans["3"].value == pytest.approx(d0, rel=0.015)
    # cached objects are not detected or segmented again; new dimensions come from cached features
    det2, seg2 = FakeDetector(), FakeSegmenter()
    rec2, _ = cv.CVTracker(det2, seg2).track_video(rows_for(video, [1, 2, 3]), SPECS, cache)
    assert det2.calls == seg2.calls == 0 and rec2["tracks"] == rec["tracks"]


def test_bare_phrase_does_not_push_qualified_phrase_off_its_instance(tmp_path):
    """'tennis ball' cached by an earlier run must not count as a different object than 'left tennis
    ball' (it used to block the left ball, so the second run tracked a speck)."""
    size = 40 * Z / CAM.f
    left = Body("ball L", ballistic([-3.0, 0.0, Z], [0.5, 0.0, 0.0]), size=size, color=(0, 0, 255))
    right = Body("ball R", ballistic([3.0, 0.0, Z], [-0.2, 0.0, 0.0]), size=size, color=(0, 0, 255))
    path = tmp_path / "two.mp4"
    render_video(str(path), [left, right], CAM, duration=2.0, fps=FPS)
    red = lambda img: _colour_mask(img, (255, 0, 0)).astype(np.uint8)  # noqa: E731

    class Det:
        name = "fake"

        def detect(self, images, query):
            out = []
            for img in images:
                n, _, st, _ = cv2.connectedComponentsWithStats(red(img))
                out.append([{"box": [float(st[i, 0]), float(st[i, 1]), float(st[i, 0] + st[i, 2]),
                                     float(st[i, 1] + st[i, 3])], "score": 0.8 - 0.01 * i, "label": "ball"}
                            for i in range(1, n)])
            return out

    class Seg:
        name = "fake-sam"

        def propagate(self, frames, prompts):   # follows the component nearest to the prompt
            for oid, (k, box) in prompts.items():
                cx = (box[0] + box[2]) / 2
                for p, img in enumerate(frames):
                    n, lab, _, cen = cv2.connectedComponentsWithStats(red(img))
                    j = 1 + int(np.argmin([abs(cen[i][0] - cx) for i in range(1, n)]))
                    cx = cen[j][0]
                    yield p, oid, lab == j, 0.9

    rows = lambda q: pd.DataFrame({"qid": q, "video_id": "two", "video_path": str(path), "fps": FPS,  # noqa: E731
                                   "video_type": "S2MC"})
    pri = Q("size", ["tennis ball"], dimension="diameter", value_si=size)
    run1 = {1: QuestionSpec(1, Q("size", ["tennis ball"], dimension="diameter", unit="cm"), pri)}
    run2 = {**run1, 2: QuestionSpec(2, Q("speed", ["left tennis ball"], unit="m/s"), pri),
            3: QuestionSpec(3, Q("speed", ["right tennis ball"], unit="m/s"), pri)}
    _, cache = cv.CVTracker(Det(), Seg()).track_video(rows([1]), run1)
    again, _ = cv.CVTracker(Det(), Seg()).track_video(rows([1, 2, 3]), run2, cache)
    fresh, _ = cv.CVTracker(Det(), Seg()).track_video(rows([1, 2, 3]), run2)
    for key in ("left tennis ball", "right tennis ball"):
        assert again["objects"][key]["box"] == fresh["objects"][key]["box"], key
    x0, y0, x1, y1 = again["objects"]["left tennis ball"]["box"]
    assert x1 - x0 > 30 and y1 - y0 > 30 and x1 < CAM.width / 2        # the whole left ball, not a speck
    assert again["objects"]["right tennis ball"]["box"][0] > CAM.width / 2


def test_ruler_calibre_prior_gives_no_track(video):
    """'ruler calibre = 1cm': the ruler's mask (or box) is not the calibre, so the prior gets no track
    and geometry fails (the direct answer is used) instead of scaling by the whole ruler."""
    spec = QuestionSpec(7, Q("speed", ["red ball"], time=1.0, unit="m/s"),
                        Q("size", ["ruler"], dimension="calibre", value_si=0.01))
    rec, _ = cv.CVTracker(FakeDetector(), FakeSegmenter()).track_video(rows_for(video, [7]), {7: spec})
    assert [t["role"] for t in rec["tracks"]["7"]] == ["target"]
    assert "prior:unmeasurable_dimension" in rec["flags"]["7"]
    ans = solve(spec, [RoleTrack.from_dict(t) for t in rec["tracks"]["7"]], (CAM.width, CAM.height), FPS)
    assert ans.value is None


class FakeTensor:
    """Stands in for a torch tensor: truth-testing it raises unless it holds exactly one value."""

    def __init__(self, v, dtype=float):
        self.v = np.asarray(v, dtype)
        self.dtype = self.v.dtype

    def tolist(self):
        return self.v.tolist()

    def __len__(self):
        return len(self.v)

    def __iter__(self):
        return iter(self.v.tolist())

    def __bool__(self):
        if self.v.size != 1:
            raise RuntimeError("Boolean value of Tensor with more than one value is ambiguous")
        return bool(self.v.item())


class _Inputs(dict):
    def to(self, device):
        return self


class StubProcessor:
    """transformers 5.11 post-processor result formats; `n` detections per image."""

    def __init__(self, kind, n):
        self.kind, self.n = kind, n

    def __call__(self, **kw):
        return _Inputs(input_ids=None)

    def _result(self, owl):
        boxes = [[10.0 + 100 * j, 10.0, 50.0 + 100 * j, 60.0] for j in range(self.n)]
        labels = FakeTensor([0] * self.n, int) if owl else ["ball"] * self.n
        return {"scores": FakeTensor([0.9 - 0.1 * j for j in range(self.n)]),
                "boxes": FakeTensor(np.reshape(boxes, (-1, 4))), "labels": labels,
                "text_labels": None if owl else ["ball"] * self.n}

    def post_process_grounded_object_detection(self, outputs, input_ids=None, threshold=0.1, text_threshold=0.2,
                                               target_sizes=None):
        return [self._result(self.kind == "owlv2") for _ in target_sizes]


@pytest.mark.parametrize("kind", ["owlv2", "gdino"])
@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_detector_handles_post_processor_formats(kind, n):
    """OWLv2's 'labels' is a tensor of class ids and 'text_labels' None: never truth-tested."""
    import contextlib
    d = object.__new__(cv.Detector)
    d.kind, d.batch, d.device, d.threshold, d.text_threshold = kind, 8, "cpu", 0.1, 0.2
    d.processor, d.model = StubProcessor(kind, n), lambda **kw: object()
    d._torch = types.SimpleNamespace(inference_mode=contextlib.nullcontext)
    out = d.detect([np.zeros((H, W, 3), np.uint8)] * 2, "tennis ball")
    assert len(out) == 2 and all(len(c) == n for c in out)
    want = "tennis ball" if kind == "owlv2" else "ball"
    assert all(c["label"] == want for c in out[0])
    assert cv.text_labels({"labels": FakeTensor([0, 1], int), "text_labels": None}) == []


def test_segmenter_auto_falls_back_when_official_fails_to_load(monkeypatch):
    torch = types.SimpleNamespace(bfloat16="bf16", float32="f32", cuda=types.SimpleNamespace(
        is_available=lambda: False, is_bf16_supported=lambda: False, empty_cache=lambda: None))

    class Predictor:
        @staticmethod
        def from_pretrained(*a, **kw):
            raise RuntimeError("hydra MissingConfigException")

    class Model:
        @classmethod
        def from_pretrained(cls, *a, **kw):
            return cls()

        def to(self, device):
            return self

        def eval(self):
            return self

    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "sam2", types.ModuleType("sam2"))
    monkeypatch.setitem(sys.modules, "sam2.sam2_video_predictor", types.SimpleNamespace(SAM2VideoPredictor=Predictor))
    monkeypatch.setitem(sys.modules, "transformers", types.SimpleNamespace(Sam2VideoModel=Model,
                                                                            Sam2VideoProcessor=Model))
    seg = cv.Segmenter("auto", device="cpu")
    assert (seg.backend, seg.name) == ("hf", "sam2-hf")
    with pytest.raises(RuntimeError, match="hydra"):
        cv.Segmenter("official", device="cpu")


def test_model_load_failure_is_remembered(video, monkeypatch):
    calls = []

    def broken(*a, **kw):
        calls.append(a)
        raise RuntimeError("CUDA error: no kernel image")

    monkeypatch.setattr(cv, "Segmenter", broken)
    trk = cv.CVTracker(FakeDetector(), "auto")
    for _ in range(2):
        with pytest.raises(cv.ModelLoadError, match="no kernel image"):
            trk.track_video(rows_for(video, [1]), SPECS)
    assert len(calls) == 1                                   # not rebuilt for every video


def _run_cv_module():
    spec = importlib.util.spec_from_file_location("run_cv", ROOT / "scripts" / "run_cv.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_run_cv_exits_nonzero_when_videos_fail(video, tmp_path, monkeypatch):
    vids = tmp_path / "videos"
    vids.mkdir()
    for v in ("vid_a", "vid_b"):
        (vids / f"{v}.mp4").write_bytes(video.read_bytes())
    csv = tmp_path / "q.csv"
    pd.DataFrame({"Unnamed: 0": [1, 2], "video_id": ["vid_a", "vid_b"], "video_source": "simulation",
                  "video_type": "S2MC", "fps": FPS, "inference_type": "SD",
                  "question": "What is the speed of the red ball at 1s in m/s?",
                  "ground_truth_prior": f"diameter of the blue ball = {SIZE:.4f}m", "depth_info": "",
                  "ground_truth_posterior": 1.2}).to_csv(csv, index=False)
    specs = tmp_path / "specs.json"
    specs.write_text(json.dumps([{**SPECS[1].to_dict(), "qid": q} for q in (1, 2)]))
    run_cv = _run_cv_module()
    argv = ["--csv", str(csv), "--video-dir", str(vids), "--specs", str(specs), "--out", str(tmp_path / "o"),
            "--solve"]

    class FlakySeg(FakeSegmenter):
        def propagate(self, frames, prompts):
            if self.calls:
                raise RuntimeError("CUDA out of memory")
            yield from super().propagate(frames, prompts)

    class BrokenSeg(FakeSegmenter):
        def propagate(self, frames, prompts):
            raise RuntimeError("CUDA out of memory")
            yield

    with pytest.raises(SystemExit, match="2 of 2 videos failed"):
        run_cv.main(argv, tracker=cv.CVTracker(FakeDetector(), BrokenSeg()))
    assert (tmp_path / "cv_geometry.csv").exists()                      # still written
    # at most --max-failed of the videos failed: a warning only
    res = run_cv.main(argv + ["--max-failed", "0.6"], tracker=cv.CVTracker(FakeDetector(), FlakySeg()))
    assert res.set_index("id").parsed_value.notna().sum() == 1
    with pytest.raises(SystemExit, match="1 of 2 videos failed"):
        run_cv.main(argv + ["--fresh"], tracker=cv.CVTracker(FakeDetector(), FlakySeg()))
    # a model that fails to load stops the run at once
    built = []

    def broken(*a, **kw):
        built.append(a)
        raise RuntimeError("hydra MissingConfigException")

    monkeypatch.setattr(cv, "Segmenter", broken)
    with pytest.raises(SystemExit, match="2 of 2 videos failed"):
        run_cv.main(argv + ["--fresh"], tracker=cv.CVTracker(FakeDetector(), "auto"))
    assert len(built) == 1


def test_run_cv_cli_resumes(video, tmp_path):
    csv = tmp_path / "q.csv"
    pd.DataFrame({"Unnamed: 0": [1, 2, 3], "video_id": video.stem, "video_source": "simulation",
                  "video_type": "S2MC", "fps": FPS, "inference_type": ["SD", "SS", "SS"],
                  "question": ["What is the speed of the red ball at 1s in m/s?",
                               "What is the diameter of the red ball in cm?",
                               "What is the initial distance between the red ball and the blue ball in meters?"],
                  "ground_truth_prior": f"diameter of the blue ball = {SIZE:.4f}m", "depth_info": "",
                  "ground_truth_posterior": [1.2, SIZE * 100, 5.15]}).to_csv(csv, index=False)
    specs = tmp_path / "specs.json"
    specs.write_text(json.dumps([s.to_dict() for s in SPECS.values()]))
    spec = importlib.util.spec_from_file_location("run_cv", ROOT / "scripts" / "run_cv.py")
    run_cv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_cv)
    out = tmp_path / "cv" / "annotate"
    argv = ["--csv", str(csv), "--video-dir", str(video.parent), "--specs", str(specs), "--out", str(out), "--solve"]
    det, seg = FakeDetector(), FakeSegmenter()
    res = run_cv.main(argv, tracker=cv.CVTracker(det, seg))
    rec = json.loads((out / f"{video.stem}.json").read_text())
    assert set(rec["tracks"]) == {"1", "2", "3"} and (tmp_path / "cv" / "cv_cache" / f"{video.stem}.json").exists()
    assert res.set_index("id").parsed_value[1] == pytest.approx(1.2, rel=0.015)
    det2, seg2 = FakeDetector(), FakeSegmenter()
    run_cv.main(argv, tracker=cv.CVTracker(det2, seg2))
    assert det2.calls == seg2.calls == 0                    # finished video skipped
    changed = {**SPECS, 2: QuestionSpec(2, Q("size", ["red ball"], dimension="radius", unit="cm"), SPECS[2].prior)}
    specs.write_text(json.dumps([s.to_dict() for s in changed.values()]))
    det3, seg3 = FakeDetector(), FakeSegmenter()
    res = run_cv.main(argv, tracker=cv.CVTracker(det3, seg3))
    assert det3.calls == seg3.calls == 0                    # changed spec: record rebuilt from the cache
    assert res.set_index("id").parsed_value[2] == pytest.approx(SIZE * 50, rel=0.015)


# ---------------------------------------------------------------- packaging

def test_imports_without_gpu_packages():
    code = ("import sys\n"
            "for m in ('torch', 'transformers', 'sam2', 'vllm'): sys.modules[m] = None\n"
            "import qp.open.cv_track as cv\n"
            "import importlib.util\n"
            "s = importlib.util.spec_from_file_location('run_cv', 'scripts/run_cv.py')\n"
            "m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
            "print(cv.SAM_MODEL)\n")
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    r = subprocess.run([sys.executable, "-c", "import sys; sys.modules['torch'] = None\n"
                        "from qp.open.cv_track import Detector; Detector()"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode != 0 and "torch" in r.stderr          # models need torch only when built


def _cells():
    nb = json.loads(NOTEBOOK.read_text())
    return nb, ["".join(c["source"]) if isinstance(c["source"], list) else c["source"] for c in nb["cells"]]


def test_notebook_is_valid_nbformat():
    nb, sources = _cells()
    assert nb["nbformat"] == 4 and nb["metadata"]["accelerator"] == "GPU"
    try:
        import nbformat
    except ImportError:
        assert all(c["cell_type"] in ("markdown", "code") for c in nb["cells"])
    else:
        nbformat.validate(nbformat.reads(NOTEBOOK.read_text(), as_version=4))
    for c, src in zip(nb["cells"], sources):
        if c["cell_type"] == "code":
            compile(re.sub(r"^\s*[!%].*$", "pass", src, flags=re.M), "<cell>", "exec")   # valid Python
    text = "\n".join(sources)
    for needle in ("nvidia-smi", "drive.mount", "userdata.get(", 'secret("GITHUB_TOKEN")', "snapshot_download",
                   "PaulineLi/QuantiPhy-validation", "quantiphy_submission_template.csv", "colab-outputs",
                   "--orphan", "RUN_NAME", "scripts/run_cv.py", "scripts/score.py", "scripts/make_submission.py"):
        assert needle in text, needle
    assert "print(GITHUB_TOKEN" not in text and "print(REPO_URL" not in text   # the token is never printed


def _cell(needle: str) -> str:
    return next(s for s in _cells()[1] if needle in s)


def test_notebook_sh_collapses_progress_bars(tmp_path, capsys):
    fn = re.search(r"^def sh\(.*?(?=^\S)", _cell("def sh("), flags=re.M | re.S).group(0)
    ns = {"io": io, "subprocess": subprocess, "LOG": str(tmp_path / "log.txt"),
          "redact": lambda s: s.replace("SECRET", "***")}
    exec(fn, ns)
    assert ns["sh"]("printf 'start\\n10%%\\r50%%\\r100%%\\nSECRET done\\r\\n'") == 0
    assert capsys.readouterr().out.splitlines()[1:] == ["start", "100%", "*** done"]
    assert (tmp_path / "log.txt").read_text().splitlines()[-3:] == ["start", "100%", "*** done"]
    assert 'os.environ["TQDM_DISABLE"] = "1"' in _cell("drive.mount")


@pytest.mark.parametrize("smi,model,caw", [
    ("NVIDIA L4, 23034", "Qwen/Qwen3-VL-4B-Instruct", False),
    ("Tesla T4, 15360", "Qwen/Qwen3-VL-4B-Instruct", False),
    ("NVIDIA A100-SXM4-40GB, 40960", "Qwen/Qwen3-VL-8B-Instruct", True),
    ("NVIDIA A100-SXM4-80GB, 81920", "Qwen/Qwen3-VL-32B-Instruct-FP8", True),
])
def test_notebook_gpu_tiers(monkeypatch, smi, model, caw):
    """An L4 (22.5 GiB) gets the 4B model and no Code-as-World-9B (neither 8B nor 9B fit vLLM there)."""
    def fake_run(cmd, **kw):
        return types.SimpleNamespace(stdout=smi if "--query-gpu" in " ".join(cmd) else "", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    ns: dict = {}
    exec(_cell("RUN_NAME = "), ns)
    exec(_cell("VRAM_GB ="), ns)
    assert ns["MODEL"] == model and ns["STAGES"]["caw"] is caw


def test_notebook_data_branch_has_no_lfs_rules():
    sync = _cell("SYNC_DATA_TO_GITHUB:")
    assert 'p.name != ".gitattributes"' in sync and '"* -filter -diff -merge -text' in sync
    assert sync.index("info\", \"attributes") < sync.index("add -A")


def test_notebook_matches_generator():
    spec = importlib.util.spec_from_file_location("build_nb", ROOT / "notebooks" / "_build_notebook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.build() == json.loads(NOTEBOOK.read_text()), "run python notebooks/_build_notebook.py"


def _flags(script: str) -> set[str]:
    spec = importlib.util.spec_from_file_location(Path(script).stem, ROOT / script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import argparse
    seen: set[str] = set()
    orig = argparse.ArgumentParser.parse_args

    def grab(self, args=None, namespace=None):
        seen.update(s for a in self._actions for s in a.option_strings)
        raise SystemExit(0)

    argparse.ArgumentParser.parse_args = grab
    try:
        mod.parse_args([]) if hasattr(mod, "parse_args") else mod.main()
    except SystemExit:
        pass
    finally:
        argparse.ArgumentParser.parse_args = orig
    return seen


def test_notebook_cli_flags_exist():
    """Every --flag the notebook passes to a repo script is defined by that script's parser."""
    _, sources = _cells()
    calls = re.findall(r"(scripts/\w+\.py)((?:[^\n\"'\\]|\\\n)*)", "\n".join(sources))
    assert calls
    for script, rest in calls:
        if not (ROOT / script).exists():
            continue
        used = set(re.findall(r"(?<![\w-])--[a-z][a-z0-9-]*", rest))
        if not used:
            continue
        missing = used - _flags(script)
        assert not missing, f"{script}: {sorted(missing)}"
    # flags kept in helper strings (LIM, EXT, CAWM) are appended to run_open_vlm.py / run_cv.py calls
    extra = re.findall(r'^(?:LIM|EXT|CAWM) = f?" (--[a-z][a-z0-9-]*)', "\n".join(sources), flags=re.M)
    assert len(extra) == 3
    for flag in extra:
        assert flag in _flags("scripts/run_open_vlm.py"), flag
    assert "--limit-videos" in _flags("scripts/run_cv.py")


def test_requirements_colab():
    lines = [ln.split("#")[0].strip() for ln in (ROOT / "requirements-colab.txt").read_text().splitlines()]
    pkgs = {re.split(r"[<>=!~@ \[]", ln, maxsplit=1)[0].lower() for ln in lines if ln}
    assert {"transformers", "accelerate", "qwen-vl-utils", "opencv-python-headless", "huggingface-hub",
            "pandas", "pyarrow", "hydra-core", "iopath"} <= {p.replace("_", "-") for p in pkgs}
    assert not pkgs & {"torch", "torchvision", "vllm"}      # preinstalled / optional heavy cell
    assert "SAM-2 @ git+https://github.com/facebookresearch/sam2.git@" in (ROOT / "requirements-colab.txt").read_text()
