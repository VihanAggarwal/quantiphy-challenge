"""Drop-position test: joint bounce-constrained fit of hops B, C, D (clean frames v21-27, v30-34 + whole-ball v35, v37-42)
under alternative second-drop positions (capture frame skipped before video 35/36/37, or none). The image step
v35->v36 is the double-length one in the raw track (38 px vs 14-15 px neighbours)."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
import common, bouncefit
TR = bouncefit.TR
# use the whole-ball (frame-difference) centre for v35
for r in ('x', 's'):
    TR[r]['35'] = dict(TR[r]['35']); TR[r]['35']['u'], TR[r]['35']['v'] = 483.9, 402.4
orig = common.cap
for name, drops in (('drop<v36 (standard)', (12, 36)), ('drop<v35', (12, 35)), ('drop<v37', (12, 37)), ('no 2nd drop', (12,))):
    bouncefit.cap = lambda n, d=None, drops=drops: orig(n, drops)
    for f in (711, 735):
        o = bouncefit.run('x', f, hops=[list(range(21, 28)), list(range(30, 36)), list(range(37, 43))], verbose=False)
        og = bouncefit.run('x', f, gfree=True, hops=[list(range(21, 28)), list(range(30, 36)), list(range(37, 43))], verbose=False)
        print(f'{name:20s} f{f}: rms {o["rms"]:.2f} max {o["maxres"]:.2f} | g free: rms {og["rms"]:.2f} g={og["g"]:.2f}')
bouncefit.cap = orig
print('--- standard clock, whole-ball v35 included, physical and model-FD values')
for r in ('x', 's'):
    for f in (711, 735):
        bouncefit.run(r, f, hops=[list(range(21, 28)), list(range(30, 36)), list(range(37, 43))])
