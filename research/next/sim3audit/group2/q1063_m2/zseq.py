from load import frames; import numpy as np, cv2, sys, json
F=frames(); bg=cv2.imread('bg.png').astype(int); sm=np.load('smooth.npy')
ids=[int(a) for a in sys.argv[2].split(',')]; out=sys.argv[1]; sc=4
W,H=180,110
tiles=[]
for i in ids:
    cx,cy=int(sm[0,i]),int(sm[1,i]); x0,y0=cx-90+10,cy-70
    c=F[i][y0:y0+H,x0:x0+W]
    d=np.abs(c.astype(int)-bg[y0:y0+H,x0:x0+W]).sum(2); d=np.clip(d*2,0,255).astype(np.uint8)
    a=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
    b=cv2.resize(cv2.cvtColor(d,cv2.COLOR_GRAY2BGR),None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    t=np.hstack([a,b])
    for gx in range(0,W,10):
        col=(0,200,255) if (x0+gx)%50==0 else (90,90,90)
        for off in (0,W*sc): cv2.line(t,(off+gx*sc,0),(off+gx*sc,H*sc),col,1)
    for gy in range(0,H,10):
        col=(0,200,255) if (y0+gy)%50==0 else (90,90,90)
        cv2.line(t,(0,gy*sc),(2*W*sc,gy*sc),col,1)
    # smooth centre marker
    for off in (0,W*sc): cv2.drawMarker(t,(off+int((sm[0,i]-x0)*sc),int((sm[1,i]-y0)*sc)),(0,0,255),cv2.MARKER_CROSS,20,2)
    cv2.putText(t,f'{i} org=({x0},{y0}) yellow lines at multiples of 50',(5,20),0,0.6,(0,0,255),2)
    tiles.append(t)
cv2.imwrite(out,np.vstack(tiles))
print([ (i,int(sm[0,i])-80,int(sm[1,i])-70) for i in ids])
