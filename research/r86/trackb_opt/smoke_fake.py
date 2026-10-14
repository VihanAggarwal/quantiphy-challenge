"""Offline smoke test of open_client + run_open_pipeline: a fake OpenAI client replays the cached Claude
record of each video (runs/val_opus_high) converted to 0-1000 coordinates; the pipeline must reproduce the
cached run's answers. No network. Usage: QP_RUNS=<scratch> .venv/bin/python research/r86/trackb_opt/smoke_fake.py"""
import json, re, sys, types
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(HERE)]
import open_client as oc
REC = ROOT / "runs/val_opus_high/val/records"

class FakeOA:
    def __init__(self):
        self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))
        self.seen = []
    def create(self, model, messages, **kw):
        user = messages[1]["content"]
        vid = re.match(r"Video (\S+?):", user[0]["text"]).group(1)
        assert "COORDINATES" in messages[0]["content"]
        assert kw["response_format"]["type"] == "json_schema"
        w, h = oc._image_size(next(b for b in user if b["type"] == "image_url")["image_url"]["url"].split(",", 1)[1])
        rec = json.loads((REC / f"{vid}.json").read_text())
        p = json.loads(json.dumps(rec["parsed"]))
        sx, sy = 1000.0 / w, 1000.0 / h          # pixels -> rel1000 (inverse of the client's conversion)
        for q in p["questions"]:
            for tr in q["tracks"]:
                for o in tr["obs"]:
                    if o.get("point"): o["point"] = [o["point"][0] * sx, o["point"][1] * sy]
                    if o.get("extent"): o["extent"] = [[e[0] * sx, e[1] * sy] for e in o["extent"]]
                    if o.get("box"): b = o["box"]; o["box"] = [b[0] * sx, b[1] * sy, b[2] * sx, b[3] * sy]
        self.seen.append((vid, w, h))
        msg = types.SimpleNamespace(content=json.dumps(p))
        return types.SimpleNamespace(id=f"fake-{vid}", choices=[types.SimpleNamespace(message=msg, finish_reason="stop")],
                                     usage=types.SimpleNamespace(prompt_tokens=1000, completion_tokens=500))

import run_open_pipeline as rop
fake = FakeOA()
orig = oc.OpenCompatClient.__init__
def init(self, *a, **k):
    k["oa_client"] = fake; orig(self, *a, **k)
oc.OpenCompatClient.__init__ = init
vids = "simulation_0170,internet_0005"
res = rop.main(["--split", "val", "--name", "smoke_open", "--videos", vids, "--effort", "high",
                "--frames", "16", "--max-frames", "32", "--workers", "2", "--model", "Qwen/fake-qwen"])
ref = pd.read_csv(ROOT / "runs/val_opus_high/val.csv").set_index("id")
m = res.set_index("id")[["parsed_value"]].join(ref[["parsed_value"]], rsuffix="_cached")
m["ratio"] = m.parsed_value / m.parsed_value_cached
print(fake.seen); print(m.round(4).to_string())
print("max |ratio-1|:", float((m.ratio - 1).abs().max()))
