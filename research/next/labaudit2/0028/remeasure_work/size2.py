import cv2, numpy as np, json
W='research/next/labaudit2/0028/remeasure_work'
tr=json.load(open(f'{W}/track_captured_0028x.json'))
def frames(v):
    c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4'); L=[]
    while True:
        ok,f=c.read()
        if not ok: break
        L.append(f)
    return L
X=frames('captured_0028x'); S=frames('captured_0028s')
def cap(k): return k + (k>=12) + (k>=36)
# s-render: blue bg; ballness = distance from bg color
bg=np.median(S[0][100:200,100:300].reshape(-1,3),axis=0)
out=[]
for i in list(range(27,36))+list(range(37,46)):
    cx,cy=int(round(tr[i]['cx'])),int(round(tr[i]['cy']))
    res=[]
    for thr in [40,80,120]:
        g=cv2.cvtColor(X[i],cv2.COLOR_BGR2GRAY).astype(float)[cy-35:cy+36,cx-25:cx+26]
        m=g>thr
        m[:, :]=m
        wr=np.sort(m.sum(1))[::-1]
        res.append(np.median(wr[:3]))
    # subpixel: sum of coverage across a row (linear in width) using normalized intensity in x render (ball ~ plateau)
    g=cv2.cvtColor(X[i],cv2.COLOR_BGR2GRAY).astype(float)[cy-35:cy+36,cx-25:cx+26]
    pl=np.percentile(g[g>80],70) if (g>80).sum()>10 else 200
    cov=np.clip(g/pl,0,1.2).sum(1)
    res.append(np.sort(cov)[::-1][:3].mean())
    # s render coverage
    s=S[i].astype(float)[cy-35:cy+36,cx-25:cx+26]
    d=np.linalg.norm(s-bg,axis=2)
    pl2=np.percentile(d[d>60],70) if (d>60).sum()>10 else 150
    cov2=np.clip(d/pl2,0,1.2).sum(1)
    res.append(np.sort(cov2)[::-1][:3].mean())
    out.append((i,cap(i),res))
    print(i,cap(i),' '.join(f'{r:6.2f}' for r in res), ' vstep %.1f'%(tr[i]['cy']-tr[i-1]['cy']))
json.dump(out,open(f'{W}/size2.json','w'))
