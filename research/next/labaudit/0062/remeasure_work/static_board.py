import cv2, numpy as np
from edgefit import *
cx=640.; cy=360.
gs=[cv2.cvtColor(cv2.imread('frames/o_%02d.png'%i),cv2.COLOR_BGR2GRAY).astype(np.float32) for i in range(0,16)]
g=np.mean(gs,axis=0)  # average static frames to cut noise
cv2.imwrite('static_board_avg.png',g.astype(np.uint8))
# approx corners
FL=(846,511); FR=(1106,598); NL=(822,678)
NRdir_near=(925,719)
res={}
for frac in [0.5,0.65]:
    far,pf,rf=edge_line(g,FL,FR,trim=(0.12,0.85),frac=frac)
    left,pl,rl=edge_line(g,FL,NL,trim=(0.12,0.88),frac=frac)
    right,pr,rr=edge_line(g,FR,(1128,690),trim=(0.15,0.95),frac=frac)
    near,pn,rn=edge_line(g,NL,(918,716),trim=(0.15,0.85),frac=frac)
    cFL=inter(far,left); cFR=inter(far,right); cNL=inter(left,near); cNR=inter(right,near)
    print('frac',frac,'FL',np.round(cFL,1),'FR',np.round(cFR,1),'NL',np.round(cNL,1),'NR',np.round(cNR,1))
    print('  resid rms far,left,right,near',[round(float(np.sqrt(np.mean(r**2))),2) for r in (rf,rl,rr,rn)],'npts',[len(x) for x in (pf,pl,pr,pn)])
    res[frac]=np.array([cFL,cFR,cNR,cNL])
np.save('static_corners.npy',res[0.5]); np.save('static_corners65.npy',res[0.65])
