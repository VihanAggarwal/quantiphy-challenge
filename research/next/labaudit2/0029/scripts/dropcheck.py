# frame-to-frame motion of the person/hand region (right side) to look for the double step near video 11->12
import cv2, numpy as np
from frames import frames
F=frames('')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in F]
regs={'person':(slice(150,720),slice(1180,1280)),'hand':(slice(560,720),slice(1050,1280)),'full':(slice(0,720),slice(0,1280))}
for k in range(1,30):
    row=[]
    for nm,(ys,xs) in regs.items():
        fl=cv2.calcOpticalFlowFarneback(G[k-1][ys,xs],G[k][ys,xs],None,0.5,3,21,3,5,1.2,0)
        mag=np.hypot(fl[...,0],fl[...,1]); row.append('%s %.2f/%.2f'%(nm,np.median(mag),np.percentile(mag,95)))
        if nm=='person': row.append('mean dx %.2f dy %.2f'%(np.median(fl[...,0][mag>0.3]) if (mag>0.3).any() else 0, np.median(fl[...,1][mag>0.3]) if (mag>0.3).any() else 0))
    print(k-1,'->',k,' | '.join(row))
