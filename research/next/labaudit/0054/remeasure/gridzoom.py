import cv2,numpy as np,sys
D='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
v=sys.argv[1]; items=sys.argv[2].split(';'); Z=int(sys.argv[3]); H=int(sys.argv[4]); name=sys.argv[5]
tiles=[]
for it in items:
    k,cx,cy=it.split(','); k=int(k); cx=int(round(float(cx))); cy=int(round(float(cy)))
    f=cv2.imread(f'{D}/{v}_{k:02d}.png')[cy-H:cy+H,cx-H:cx+H]
    f=cv2.resize(f,None,fx=Z,fy=Z,interpolation=cv2.INTER_NEAREST)
    for g in range(0,2*H+1,2):
        col=(0,0,255) if g%10==0 else (90,90,90)
        cv2.line(f,(g*Z,0),(g*Z,2*H*Z),col,1); cv2.line(f,(0,g*Z),(2*H*Z,g*Z),col,1)
    cv2.putText(f,f'{v}{k} x0={cx-H} y0={cy-H}',(3,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
    tiles.append(f)
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/{name}.png',np.hstack(tiles))
