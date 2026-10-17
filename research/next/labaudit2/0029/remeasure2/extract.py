import cv2,sys,os
vid=sys.argv[1]; tag=sys.argv[2]; frames=[int(x) for x in sys.argv[3].split(',')]
c=cv2.VideoCapture(vid); i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames:
        cv2.imwrite(f'img/{tag}_{i:02d}.png', f)
    i+=1
