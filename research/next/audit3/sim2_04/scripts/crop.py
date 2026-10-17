import cv2, numpy as np, sys
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_04/'
i=int(sys.argv[1]); fr=[int(x) for x in sys.argv[2].split(',')]
x0,y0,x1,y1=[int(v) for v in sys.argv[3].split(',')]
scale=float(sys.argv[4]) if len(sys.argv)>4 else 1.0
out=sys.argv[5] if len(sys.argv)>5 else f'crop_{i}.png'
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{i:04d}.mp4')
n=0; ims=[]
while True:
    ok,f=c.read()
    if not ok: break
    if n in fr:
        im=f[y0:y1,x0:x1].copy()
        # grid every 50 px
        for gx in range((x0//50+1)*50, x1, 50):
            cv2.line(im,(gx-x0,0),(gx-x0,8 if gx%100 else 20),(0,0,255),1)
        for gy in range((y0//50+1)*50, y1, 50):
            cv2.line(im,(0,gy-y0),(8 if gy%100 else 20,gy-y0),(0,0,255),1)
        im=cv2.resize(im,None,fx=scale,fy=scale)
        cv2.putText(im,f'{i} f{n} x0={x0} y0={y0}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        ims.append(im)
    n+=1
cv2.imwrite(W+out,np.vstack(ims) if len(ims)>1 else ims[0])
