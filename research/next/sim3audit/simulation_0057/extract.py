import cv2, sys, os
vid, frames = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
scale = float(sys.argv[3]) if len(sys.argv)>3 else 0.6
out = '/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0057/frames'
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
i=0
while True:
    ok, im = c.read()
    if not ok: break
    if i in frames:
        im2 = cv2.resize(im, None, fx=scale, fy=scale) if scale!=1 else im
        cv2.imwrite(f'{out}/{vid}_f{i:03d}.png', im2)
    i+=1
print('n',i)
