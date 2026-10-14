"""Skeptic check of the 'TTA multi-keyframe SAM-2 seeding' proposal: how often does the existing cvq SAM 2 track
disagree with Qwen's own boxes (proxy for seeding failures that re-seeding could fix)? Test inputs only."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/home/user/quantiphy-challenge'); sys.path.insert(0, str(ROOT))
from qp.data import load_split
TB = Path('/tmp/claude-0/tb3/x/trackb_v1')
rows = []
for split in ('test', 'val'):
    for f in sorted((TB / split / 'cvq/annotate').glob('*.json')):
        r = json.load(open(f))
        for k, o in r['objects'].items():
            rows.append(dict(split=split, vid=r['video_id'], obj=k, prompt=o.get('prompt'), agree=o.get('agree'),
                             nframes=o.get('n_frames'), flags=','.join(o.get('flags', [])),
                             npf=len(o.get('prompt_frames', []) or [])))
d = pd.DataFrame(rows)
d['src'] = d.vid.str.split('_').str[0]
for (s, src), g in d.groupby(['split', 'src']):
    a = g.agree.dropna()
    print(s, src, 'objects', len(g), 'qwen-prompted', (g.prompt == 'qwen').sum(), 'agree n', len(a),
          'agree<0.5', round((a < .5).mean(), 3), 'agree<0.8', round((a < .8).mean(), 3), 'agree==1', round((a >= .999).mean(), 3))
d.to_csv(ROOT / 'research/r86/skeptic_tta/objects_agree.csv', index=False)
