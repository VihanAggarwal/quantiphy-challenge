import sys, numpy as np, cv2
sys.argv = ['x', '1459', '18.4', '0,24,71']
src = open('/home/user/quantiphy-challenge/research/next/sim3audit/group5/scripts/star_fit.py').read().split('best = None')[0]
exec(src)
g = np.array([np.deg2rad(60), 0.5, 0.06, 0.08, 1.0])
outs = []
for i, k in enumerate(FRAMES):
    r = render(k, g, pf0[3*i:3*i+3])
    print(k, 'model sum', r.sum(), 'obs sum', obs[k].sum(), 'Z', pf0[3*i])
    outs.append(np.hstack([obs[k], r]))
cv2.imwrite('/home/user/quantiphy-challenge/research/next/sim3audit/group5/frames/star_dbg.png', (np.vstack(outs) * 255).astype(np.uint8))
