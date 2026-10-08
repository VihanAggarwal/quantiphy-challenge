import importlib.util
import math
from pathlib import Path

import pandas as pd
import pytest

from qp import combine as C

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("rule,geo,direct,flags,is_3d,src,method,expected", [
    # 2D: geometry unless a blow-up or > 10x off the direct answer (every rule)
    ("assumed_src", 2.0, 2.4, "", False, "internet", "2d_scale", ("geometry:2d_scale", 2.0)),
    ("assumed_src", 25.0, 2.4, "", False, "simulation", "2d_scale", ("direct", 2.4)),
    ("assumed_src", 2.0, 2.4, "geo_rejected_implausible", False, "lab", "2d_scale", ("direct", 2.4)),
    ("3d_direct", 2.0, 2.4, "", False, "lab", "2d_scale", ("geometry:2d_scale", 2.0)),
    # 3D, known camera (lab): geometry unless it rests on an assumed range / focal length
    ("assumed_src", 2.0, 2.4, "geo:f_camera_prior", True, "lab", "3d_focal_from_prior", ("geometry:3d_focal_from_prior", 2.0)),
    ("assumed_src", 2.0, 2.4, "geo:target_depth_from_prior", True, "lab", "3d_focal_from_prior", ("direct", 2.4)),
    ("assumed_src", 2.0, 2.4, "geo:default_focal", True, "simulation", "3d_default_focal", ("direct", 2.4)),
    ("assumed", 2.0, 2.4, "geo:default_focal", True, "simulation", "3d_default_focal", ("direct", 2.4)),
    # ... a known camera fixes f: assumptions about the prior (used only for f) do not count
    ("assumed_src", 2.0, 2.4, "geo:default_focal;geo:prior_depth_assumed_scene_median", True, "lab",
     "3d_default_focal", ("geometry:3d_default_focal", 2.0)),
    ("assumed_src", 2.0, 2.4, "geo:default_focal;geo:target_depth_scene_median", True, "lab",
     "3d_default_focal", ("direct", 2.4)),
    ("assumed", 2.0, 2.4, "geo:target_depth_claude_estimate", True, "lab", "3d_focal_from_prior", ("direct", 2.4)),
    ("assumed_src", 2.0, 2.4, "geo:3d_without_depth", True, "lab", "2d_scale", ("direct", 2.4)),
    # 3D without a known camera: direct (assumed_src), geometry (assumed)
    ("assumed_src", 2.0, 2.4, "", True, "simulation", "3d_focal_from_prior", ("direct", 2.4)),
    ("assumed", 2.0, 2.4, "", True, "simulation", "3d_focal_from_prior", ("geometry:3d_focal_from_prior", 2.0)),
    ("geo", 2.0, 2.4, "geo:target_depth_from_prior", True, "simulation", "3d_focal_from_prior", ("geometry:3d_focal_from_prior", 2.0)),
    ("3d_direct", 2.0, 2.4, "", True, "lab", "3d_focal_from_prior", ("direct", 2.4)),
    # a camera_distance lookup keeps geometry; a missing answer falls back to the other one
    ("3d_direct", 2.0, 2.4, "", True, "simulation", "depth_direct", ("geometry:depth_direct", 2.0)),
    ("assumed_src", 2.0, None, "", True, "simulation", "3d_focal_from_prior", ("geometry:3d_focal_from_prior", 2.0)),
    ("assumed_src", None, 2.4, "", False, "lab", "", ("direct", 2.4)),
    ("assumed_src", math.nan, -1.0, "", False, "lab", "", ("none", math.nan)),
])
def test_choose(rule, geo, direct, flags, is_3d, src, method, expected):
    value, how, _ = C.choose(geo, direct, flags, is_3d, src, method, rule)
    assert how == expected[0]
    assert (math.isnan(value) and math.isnan(expected[1])) or value == expected[1]


def test_choose_flags_and_csv_method_strings():
    v, how, added = C.choose(25.0, 2.0, "geo:x;geo_direct_disagree", False, "", "geometry:2d_scale", "geo")
    assert how == "direct" and added == ["geo_direct_disagree", "geo_rejected_disagree"]
    _, how, added = C.choose(2.0, 2.2, ["geo:target2_depth_from_target"], True, "lab", "3d_focal_from_prior")
    assert how == "direct" and added == ["geo_rejected_assumed_depth"]
    with pytest.raises(ValueError):
        C.choose(1.0, 1.0, "", False, rule="bogus")


def test_combine_values_log_median():
    assert C.combine_values([1.0, 4.0]) == pytest.approx(2.0)
    assert C.combine_values([1.0, 100.0, 2.0]) == pytest.approx(2.0)
    assert C.combine_values([math.nan, None, -1, 3.0]) == pytest.approx(3.0)
    assert math.isnan(C.combine_values([math.nan]))


META = pd.DataFrame({"qid": [1, 2, 3, 4], "video_id": ["a", "a", "b", "b"], "video_type": ["V2SC", "V2SC", "S3SC", "S3SC"],
                     "video_source": ["internet", "internet", "simulation", "simulation"],
                     "category": ["D2", "S2", "S3", "S3"], "answer": [2.0, 1.0, 5.0, 3.0]})


def _run(geo, direct, flags=("", "", "", "")):
    return pd.DataFrame({"id": [1, 2, 3, 4], "parsed_value": geo, "geo_value": geo, "direct_value": direct,
                         "method": ["geometry:2d_scale"] * 2 + ["geometry:3d_focal_from_prior"] * 2,
                         "flags": list(flags)})


def test_select_and_combine_tables():
    r1 = _run([2.0, 1.0, 9.0, 1.0], [2.2, 1.1, 5.0, 3.1])
    r2 = _run([2.2, math.nan, 9.0, 1.0], [2.0, 1.2, 5.5, 2.9])
    s1 = C.select_table(r1, META, "assumed_src")
    assert s1.parsed_value.tolist() == [2.0, 1.0, 5.0, 3.1]        # 3D simulation -> direct
    assert s1.method.tolist()[2:] == ["direct", "direct"] and s1.geo_method.tolist()[2] == "3d_focal_from_prior"
    assert C.select_table(r1, META, "geo").parsed_value.tolist() == [2.0, 1.0, 9.0, 1.0]
    out = C.combine_tables([s1, C.select_table(r2, META, "assumed_src")])
    assert out.parsed_value.tolist() == pytest.approx([math.sqrt(2.0 * 2.2), math.sqrt(1.0 * 1.2),
                                                       math.sqrt(5.0 * 5.5), math.sqrt(3.1 * 2.9)])
    assert out.n_runs.tolist() == [2, 2, 2, 2]


def test_lovo_cv_picks_the_rule_that_wins_out_of_fold():
    meta = pd.concat([META.assign(qid=META.qid + 10 * k, video_id=META.video_id + str(k)) for k in range(3)])
    runs = [pd.concat([_run([2.0, 1.0, 9.0, 1.0], [2.5, 1.3, 5.0, 3.0]).assign(id=lambda d, k=k: d.id + 10 * k)
                       for k in range(3)])]
    cv = C.lovo_cv(runs, meta, rules=("geo", "3d_direct"))
    assert set(cv["chosen"].values()) == {"3d_direct"} and cv["per_run"][0] == pytest.approx(1.0)
    assert cv["in_sample"]["3d_direct"] > cv["in_sample"]["geo"]


def test_combine_runs_script(tmp_path, monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location("combine_runs", ROOT / "scripts" / "combine_runs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "load_split", lambda split: META)
    paths = []
    for k, run in enumerate([_run([2.0, 1.0, 9.0, 1.0], [2.2, 1.1, 5.0, 3.1]),
                             _run([2.2, 1.0, 9.0, 1.0], [2.0, 1.2, 5.5, 2.9])]):
        p = tmp_path / f"r{k}" / "val.csv"
        p.parent.mkdir()
        run.to_csv(p, index=False)
        paths.append(str(p))
    out = mod.main([*paths, "--split", "val", "--out", str(tmp_path / "c.csv"), "--cv"])
    assert (tmp_path / "c.csv").exists() and list(pd.read_csv(tmp_path / "c.csv").columns[:2]) == ["id", "parsed_value"]
    assert out.parsed_value.notna().all()
    text = capsys.readouterr().out
    assert "MRA combined (2 runs)" in text and "LOVO CV" in text
