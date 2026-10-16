import cv2, numpy as np
from edgefit import edge_line, inter
img=cv2.imread('c29_med_late.png'); g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
lft,pl,rl=edge_line(g,(421,345),(421,448),trim=(0.05,0.95),half=10)
rgt,pr,rr=edge_line(g,(921,350),(921,460),trim=(0.05,0.95),half=10)
top,pt,rt=edge_line(g,(430,334),(910,344),trim=(0.08,0.92),half=8)
back=np.load('c29_back_line.npy')
C=np.load('c29_table_corners.npy')
print('rms',[round(float(np.sqrt(np.mean(r**2))),2) for r in (rl,rr,rt)],[len(p) for p in (pl,pr,pt)])
TL=inter(lft,top); TR=inter(rgt,top)
# board edges at the table back-edge line
BLb=inter(lft,back); BRb=inter(rgt,back)
print('board TL',np.round(TL,1),'TR',np.round(TR,1),' at back-edge line: left',np.round(BLb,1),'right',np.round(BRb,1))
print('table back edge corners',np.round(C[3],1),np.round(C[2],1),'len px',round(np.linalg.norm(C[2]-C[3]),1))
wb=np.linalg.norm(BRb-BLb); wt=np.linalg.norm(TR-TL)
print('board width px at back-edge line',round(wb,1),'at top',round(wt,1))
print('ratio-method L (board at table back-edge depth) = %.1f cm'%(76.0*wb/np.linalg.norm(C[2]-C[3])))
f=711.; 
for z in [1.157,1.166,1.18]:
    print(' fronto-parallel z=%.3f: L=%.1f cm (bottom-row px) / %.1f (top)'%(z,wb*z/f*100,wt*z/f*100))
