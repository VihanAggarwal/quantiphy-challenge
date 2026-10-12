"""Contact sheet of a video's frames with Claude's tracks drawn (sent-frame pixels / scale)."""
import json, sys, cv2, numpy as np
vid = sys.argv[1]; out = sys.argv[2]; nf = int(sys.argv[3]) if len(sys.argv) > 3 else 6
run = sys.argv[4] if len(sys.argv) > 4 else 'runs/test_v1_high_854/test/records'
r = json.load(open(f'{run}/{vid}.json')); m = r['meta']; s = m['scale']
cap = cv2.VideoCapture(f'data/QuantiPhy/{vid}.mp4'); n = int(cap.get(7))
idx = np.linspace(0, n - 1, nf).astype(int)
cols = [(0,0,255),(0,255,0),(255,0,0),(0,255,255),(255,0,255),(255,255,0)]
tiles = []
for fi in idx:
    cap.set(1, fi); ok, im = cap.read()
    if not ok: continue
    for qi, q in enumerate(r['parsed']['questions']):
        for ti, t in enumerate(q['tracks']):
            c = cols[(qi * 2 + ti) % len(cols)]
            for o in t['obs']:
                if o.get('frame') is None or abs(o['frame'] - fi) > 0: continue
                if o.get('point'): cv2.circle(im, tuple(int(v / s) for v in o['point']), 8, c, 3)
                if o.get('box'): b = [int(v / s) for v in o['box']]; cv2.rectangle(im, b[:2], b[2:], c, 2)
                if o.get('extent'): e = o['extent']; cv2.line(im, tuple(int(v / s) for v in e[0]), tuple(int(v / s) for v in e[1]), c, 2)
    cv2.putText(im, f'{fi} t={fi/m["fps"]:.2f}', (20, 60), 0, 2, (0, 255, 255), 4)
    h, w = im.shape[:2]; k = 640 / max(h, w)
    tiles.append(cv2.resize(im, (int(w * k), int(h * k))))
h = max(t.shape[0] for t in tiles); w = max(t.shape[1] for t in tiles)
tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, w - t.shape[1], 0) for t in tiles]
rows = [np.hstack(tiles[i:i + 3] + [np.zeros_like(tiles[0])] * (3 - len(tiles[i:i + 3]))) for i in range(0, len(tiles), 3)]
cv2.imwrite(out, np.vstack(rows))
