import cv2,sys,os
v=sys.argv[1]; tag=sys.argv[2]; idx=[int(x) for x in sys.argv[3].split(',')]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in idx: cv2.imwrite(f'frames/{tag}_{i:03d}.png',f)
    i+=1
