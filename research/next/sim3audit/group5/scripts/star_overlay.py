import sys, json, numpy as np, cv2
jf = sys.argv[1]; script = sys.argv[2]
J = json.load(open(jf))
sys.argv = ['x', str(J['F']), str(J['theta']), ','.join(map(str, J['frames']))]
src = open(script).read().split('best = None')[0]
exec(src)
g = np.array(J['g']); pf = np.array(J['pf'])
rows = []
for i, k in enumerate(J['frames']):
    m = render(k, g, pf[i]); o = obs[k]
    diff = 0.5 + 0.5 * (m - o)
    rows.append(np.hstack([o, m, diff]))
img = (np.vstack(rows[:6]) * 255).astype(np.uint8)
img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
out = jf.replace('.json', '_overlay.png').replace('/group5/', '/group5/frames/')
cv2.imwrite(out, img); print(out)
