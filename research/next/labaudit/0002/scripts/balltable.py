import cv2, numpy as np
bg=cv2.imread('frames/f48.png').astype(float)
bgs=np.median(np.stack([cv2.imread(f'frames/f{i:02d}.png').astype(float) for i in [45,46,47,48]]),0)
for i in [36,37,38,39,40]:
    f=cv2.imread(f'frames/f{i:02d}.png').astype(float)
    d=np.linalg.norm(f-bgs,axis=2)
    d=cv2.GaussianBlur(d,(3,3),0)
    sub=d[400:500,560:680]
    m=sub>0.5*np.percentile(sub,99.5)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    pk=np.percentile(sub[lab==k],90)
    # per-row widths at 50% of peak with subpixel
    ws=[]
    for yy in range(y,y+h):
        row=sub[yy]; lvl=0.5*pk
        idx=np.nonzero(row>lvl)[0]
        if len(idx)<2: continue
        a0=idx[0]; b0=idx[-1]
        xa=a0-1+(lvl-row[a0-1])/(row[a0]-row[a0-1]); xb=b0+(row[b0]-lvl)/(row[b0]-row[b0+1])
        ws.append((yy+400,xb-xa,560+(xa+xb)/2))
    ws=np.array(ws)
    top=np.sort(ws[:,1])[-5:]
    print(i,'bbox',x+560,y+400,w,h,'peak',round(pk),'max widths',np.round(top,1),'centre row',ws[np.argmax(ws[:,1])][[0,2]])
    cv2.imwrite(f'diff_{i}.png',cv2.resize(np.clip(sub*3,0,255).astype(np.uint8),None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST))
