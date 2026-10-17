import cv2, sys, os
vid, frames = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
out = '/home/user/quantiphy-challenge/research/next/sim3audit/group4/frames'
cap = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if i in frames:
        cv2.imwrite(f'{out}/{vid}_f{i:03d}.png', fr)
    i += 1
print('done', i)
