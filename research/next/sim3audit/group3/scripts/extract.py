import cv2, sys, os
v=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.5
out=f'/home/user/quantiphy-challenge/research/next/sim3audit/group3/frames/{v}'; os.makedirs(out,exist_ok=True)
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames:
        g=cv2.resize(f,None,fx=scale,fy=scale) if scale!=1 else f
        cv2.imwrite(f'{out}/f{i:03d}.png',g)
    i+=1
print(i)
