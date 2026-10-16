"""Measure the 'distance between A and B = centre-to-centre' convention on validation internet rows (labels used only
to MEASURE the convention; no test row is set from a validation label). Gap alternatives = centre minus the objects'
own extent along the line, from the agent notes / stated priors (billiard ball 57.2 mm; cars ~4.8 m long but the
roundabout pair is oriented ~45 deg -> ~3.4 m; people ~0.45 m shoulder width; road-sign boards ~0.6 m)."""
import sys
import numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge')
from qp.mra import item_scores
rows = [  # qid, clip, label, agent centre answer, approx gap alternative
    (2165, 'internet_0005 signs', 4.77, 4.90, 4.90 - 0.6),
    (2205, 'internet_0013 cars', 27.0, 25.99, 25.99 - 3.4),
    (2232, 'internet_0019 people', 4.52, 4.35, 4.35 - 0.45),
    (2272, 'internet_0027 balls t0', 14.74, 14.55, 14.55 - 5.72),
    (2275, 'internet_0027 balls end', 18.04, 17.70, 17.70 - 5.72),
]
gt = np.array([r[2] for r in rows]); c = np.array([r[3] for r in rows]); g = np.array([r[4] for r in rows])
for r, sc, sg in zip(rows, item_scores(c, gt), item_scores(g, gt)):
    print(f'{r[0]} {r[1]:24s} label {r[2]:6.2f} centre {r[3]:6.2f} ({sc:.1f})  gap {r[4]:6.2f} ({sg:.1f})')
print('mean item: centre', item_scores(c, gt).mean().round(3), ' gap', item_scores(g, gt).mean().round(3),
      ' mean |log| centre', np.abs(np.log(c / gt)).mean().round(3))
