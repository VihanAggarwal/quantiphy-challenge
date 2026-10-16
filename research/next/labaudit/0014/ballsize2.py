import cv2, numpy as np
for R in ['rs','rx','ro']:
    bg=np.median(np.stack([cv2.imread(f'frames/{R}_{i:02d}.png').astype(np.float32) for i in range(36,49)]),0)
    for f in [8,9,10,12,13,14,15,16]:
        im=cv2.imread(f'frames/{R}_{f:02d}.png').astype(np.float32)
        d=np.abs(im-bg).sum(2)
        d[:, :500]=0; d[:,600:]=0; d[:270]=0; d[480:]=0
        # centre row = row with max horizontal extent sum
        ys,xs=np.where(d>40)
        if len(ys)==0: continue
        cy=int(np.median(ys))
        res=[]
        for y in range(cy-3,cy+4):
            p=d[y,500:600]; pk=np.percentile(p[p>40],70) if (p>40).sum()>5 else 0
            thr=pk/2
            ins=np.where(p>thr)[0]
            if len(ins)<5: continue
            i0,i1=ins.min(),ins.max()
            x0=i0-1+(thr-p[i0-1])/(p[i0]-p[i0-1]); x1=i1+(p[i1]-thr)/(p[i1]-p[i1+1])
            res.append(x1-x0)
        print(R,f,'cy',cy,'half-max widths',np.round(res,1),'max',round(max(res),1) if res else None)
