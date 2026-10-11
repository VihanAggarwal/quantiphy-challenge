"""Shared loaders for the size-convention study (research/sizeconv). CPU only, no API calls."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import run_claude as rc  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp.data import load_split  # noqa: E402

REC = {"test": ROOT / "runs/test_v1_high_854/test/records",
       "val_hires": ROOT / "runs/val_hr_v1_high/val_hires/records"}
RAW = {"test": ROOT / "runs/test_v1_high_854/test.csv",
       "val_hires": ROOT / "runs/val_hr_v1_high/val_hires.csv"}

# articulated / deformable objects whose labelled size is an envelope (world AABB over the animation,
# wingspan = max in flight, human = T-pose height)
ARTIC = re.compile(
    r"\b(birds?|eagles?|hawks?|falcons?|owls?|parrots?|pigeons?|doves?|crows?|ravens?|seagulls?|gulls?|swans?|geese|goose|"
    r"ducks?|flamingos?|pelicans?|penguins?|sparrows?|hummingbirds?|butterfl(?:y|ies)|moths?|bees?|wasps?|dragonfl(?:y|ies)|"
    r"bats?|dragons?|wings?|wingspan|"
    r"horses?|ponies|pony|zebras?|cats?|kittens?|dogs?|pupp(?:y|ies)|wolf|wolves|fox(?:es)?|deer|elk|moose|cows?|bulls?|"
    r"sheep|goats?|pigs?|lions?|tigers?|leopards?|cheetahs?|bears?|elephants?|giraffes?|camels?|rabbits?|bunn(?:y|ies)|"
    r"mice|mouse|rats?|squirrels?|monkeys?|apes?|gorillas?|kangaroos?|frogs?|toads?|lizards?|snakes?|crocodiles?|"
    r"alligators?|turtles?|dinosaurs?|t-?rex|raptors?|spiders?|ants?|insects?|animals?|creatures?|"
    r"fish(?:es)?|sharks?|whales?|dolphins?|octop(?:us|i)|jellyfish|squids?|seals?|"
    r"persons?|people|man|men|woman|women|human|humans|boy|girl|child|children|kid|kids|astronauts?|pedestrians?|"
    r"walkers?|runners?|jogger|athletes?|players?|dancers?|soldiers?|knights?|characters?|figures?|robots?|mannequins?|"
    r"skaters?|skiers?|cyclists?|riders?|swimmers?|divers?|gymnasts?|zombies?|ninjas?|warriors?|"
    r"flags?|banners?|cloth|cape|curtains?|tails?)\b", re.I)


def load(split: str):
    """(questions df indexed by qid, {qid: Annotation}, {video_id: record})."""
    df = load_split(split)
    recs = {}
    for p in sorted(REC[split].glob("*.json")):
        r = json.loads(p.read_text())
        if r and r.get("meta"):
            recs[r["video_id"]] = r
    prec = rc.prepare_records(df, recs)
    anns = ca.load_annotations(prec)
    return df.set_index("qid"), anns, recs


def read_csv(path, index):
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    return d["parsed_value"].astype(float).reindex(index)


def is_artic(*texts) -> bool:
    return any(ARTIC.search(str(t or "")) for t in texts)
