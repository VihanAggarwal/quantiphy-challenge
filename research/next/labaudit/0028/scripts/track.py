import cv2, numpy as np
out='/home/user/quantiphy-challenge/research/next/labaudit/0028/frames'
for i in range(49):
    f=cv2.imread(f'{out}/captured_0028x_{i:02d}.png').astype(int)
    g=f.mean(2); 
    # white ball: high brightness, low saturation
    m=(g>150)&(np.abs(f[:,:,0]-f[:,:,2])<40)
    m[680:,:]=False
    ys,xs=np.nonzero(m)
    if len(xs)==0: print(i,'none'); continue
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    comps=[(st[k,4],k) for k in range(1,n) if st[k,4]>15]
    s=' '.join(f'[a={st[k,4]} c=({cen[k][0]:.1f},{cen[k][1]:.1f}) bb={st[k,0]},{st[k,1]},{st[k,2]}x{st[k,3]}]' for a,k in sorted(comps,reverse=True)[:3])
    print(i, s)
