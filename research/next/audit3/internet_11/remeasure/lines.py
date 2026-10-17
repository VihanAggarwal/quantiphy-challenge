import cv2, numpy as np
bg=cv2.imread('research/next/audit3/internet_11/remeasure/png/bg47_ref15.png').astype(np.float32)
B,G,R=bg[...,0],bg[...,1],bg[...,2]
# red line: dark red -> low G; wood: G high. white: high B
def edges(prof, thr):
    m=prof>thr
    # return subpixel crossings
    xs=[]
    for i in range(len(prof)-1):
        if (prof[i]-thr)*(prof[i+1]-thr)<0:
            xs.append(i+(thr-prof[i])/(prof[i+1]-prof[i]))
    return xs
print('vertical lines: row, leftred(L,R,w), white(L,R,w), rightred(L,R,w)')
for y in range(520,1080,40):
    rowG=G[y-3:y+4].mean(axis=0); rowB=B[y-3:y+4].mean(axis=0); rowR=R[y-3:y+4].mean(axis=0)
    red=-(rowG)  # dark -> high
    # left red near 150-330
    out=[y]
    for (a,b) in [(150,330),(1650,1850)]:
        seg=rowG[a:b]; lo=np.percentile(seg,3); hi=np.median(seg); thr=(lo+hi)/2
        xs=edges(-seg,-thr)
        if len(xs)>=2: out.append((a+xs[0],a+xs[-1],xs[-1]-xs[0]))
        else: out.append(None)
    # white: high blue relative to red
    w=(rowB-rowR)
    a,b=1100,1300; seg=w[a:b]; lo=np.median(seg); hi=np.percentile(seg,97); thr=(lo+hi)/2
    xs=edges(seg,thr)
    out.insert(2,(a+xs[0],a+xs[-1],xs[-1]-xs[0]) if len(xs)>=2 else None)
    print(out[0],' '.join('(%.1f,%.1f,%.1f)'%t if t else 'None' for t in out[1:]))
print('top red line vertical thickness at columns')
for x in range(300,1900,100):
    colG=G[:,x-3:x+4].mean(axis=1)
    seg=colG[400:560]; lo=np.percentile(seg,3); hi=np.median(seg); thr=(lo+hi)/2
    ys=edges(-seg,-thr)
    print(x, ['%.1f'%(400+v) for v in ys], 'w %.1f'%(ys[-1]-ys[0]) if len(ys)>=2 else '')
