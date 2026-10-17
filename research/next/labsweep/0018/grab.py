import cv2,sys
v=sys.argv[1]; idxs=[int(x) for x in sys.argv[2].split(',')]
out=sys.argv[3]
scale=float(sys.argv[4]) if len(sys.argv)>4 else 1.0
crop=sys.argv[5] if len(sys.argv)>5 else None
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
frames=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in idxs: frames.append((i,f))
    i+=1
for i,f in frames:
    if crop:
        x0,y0,x1,y1=[int(t) for t in crop.split(',')]
        f=f[y0:y1,x0:x1]
    if scale!=1: f=cv2.resize(f,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC if scale>1 else cv2.INTER_AREA)
    cv2.imwrite(f'{out}_{i:02d}.png',f)
