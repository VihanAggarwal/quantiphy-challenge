"""Extract selected frames (PNG) from a clip. usage: extract.py video_id frame[,frame...] [scale]"""
import sys, cv2, os
vid = sys.argv[1]; frames = [int(x) for x in sys.argv[2].split(',')]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
out = '/home/user/quantiphy-challenge/research/next/sim3audit/group2/frames'
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
i = 0
want = set(frames)
while want:
    ok, f = c.read()
    if not ok: break
    if i in want:
        if scale != 1.0: f = cv2.resize(f, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{out}/{vid}_{i:03d}.png', f); want.discard(i)
    i += 1
print('done', vid, sorted(frames))
