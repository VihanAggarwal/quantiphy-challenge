from common import *
O=load(''); X=load('x'); Sr=load('s')
# 1) render alignment: compare person/box positions in o vs s vs x via edge correlation in box region
def edges(img): return cv2.Canny(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY),50,150).astype(float)
for name,R in [('s',Sr),('x',X)]:
    a=edges(O[0][200:320,440:600]); b=edges(R[0][200:320,440:600])
    best=None
    for dy in range(-4,5):
        for dx in range(-4,5):
            c=(np.roll(np.roll(b,dy,0),dx,1)*a).sum()
            if best is None or c>best[0]: best=(c,dx,dy)
    print('render',name,'best shift vs original (dx,dy)',best[1:])
# 2) held box width/height per frame from the original render: box is bright (>170) vs wall (~125-140)
res=[]
for i in range(0,28):
    g=O[i].astype(float).mean(2)
    # width: rows 255..270 (mid-box, above the forearm/logo), bright run containing x=480
    ws=[]
    for y in range(252,272):
        row=g[y,455:510]
        b=row>170
        # run containing index of x=480
        k=480-455
        if not b[k]: continue
        l=k
        while l>0 and b[l-1]: l-=1
        r=k
        while r<len(b)-1 and b[r+1]: r+=1
        ws.append(r-l+1)
    # height: column x=484..488 bright run containing y=265
    hs=[]
    for x in range(482,490):
        col=g[225:305,x]; b=col>165; k=265-225
        if not b[k]: continue
        t=k
        while t>0 and b[t-1]: t-=1
        bo=k
        while bo<len(b)-1 and b[bo+1]: bo+=1
        hs.append((t+225,bo+225))
    res.append((i,np.median(ws) if ws else None, hs[len(hs)//2] if hs else None))
for r in res: print(r)
