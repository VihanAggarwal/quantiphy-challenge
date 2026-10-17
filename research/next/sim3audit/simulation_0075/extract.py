import cv2, sys, os
out = '/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0075/frames'
clip = sys.argv[1]; frames = [int(x) for x in sys.argv[2].split(',')]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
cap = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{clip}.mp4')
i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if i in frames:
        if scale != 1: fr = cv2.resize(fr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{out}/{clip}_f{i:02d}.png', fr)
    i += 1
print('done', i)
