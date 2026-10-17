import cv2,sys
v=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.5
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames:
        g=cv2.resize(f,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'png/{v}_f{i:02d}.png',g)
    i+=1
