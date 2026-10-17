import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0024x.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
f=fr[10]
# sample pixels: book top approx (half-scale 390,185)->full (780,370)? print a grid
for y in range(340,420,8):
    print(y, ' '.join('%3d,%3d,%3d'%tuple(f[y,x][::-1]) for x in range(700,860,16)))
