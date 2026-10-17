import cv2, sys, os
vid, frames = sys.argv[1], sys.argv[2]
out = '/home/user/quantiphy-challenge/research/next/sim3audit/group5/frames'
cap = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = cap.get(cv2.CAP_PROP_FPS)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(vid, n, fps, W, H)
if frames == 'info': sys.exit()
fs = set(int(x) for x in frames.split(','))
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if i in fs:
        if scale != 1.0: fr = cv2.resize(fr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{out}/{vid}_f{i:03d}.png', fr)
    i += 1
print('done', i)
