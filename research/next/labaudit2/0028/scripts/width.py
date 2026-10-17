import cv2, numpy as np, json
# sub-pixel horizontal half-max width of the ball on the x render (black background), per row, median over central rows
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/track.json'))
res={}
for V in ['captured_0028x','captured_0028s']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{V}.mp4'); F=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float))
    out=[]
    for i,g in enumerate(F):
        r=T[V][i]
        if r is None: out.append(None); continue
        top,bot=r['top'],r['bot']; cx=int(round(r['cx']))
        ws=[]; 
        for y in range(top,bot+1):
            p=g[y,cx-25:cx+26]
            bg=np.median(np.r_[g[y,cx-40:cx-28],g[y,cx+28:cx+40]])
            pk=np.percentile(p,95)
            if pk-bg<60: continue
            h=bg+0.5*(pk-bg)
            idx=np.nonzero(p>h)[0]
            if len(idx)<3: continue
            a,b=idx[0],idx[-1]
            # subpixel crossings
            xl=a-1+(h-p[a-1])/(p[a]-p[a-1]) if p[a]!=p[a-1] else a
            xr=b+(p[b]-h)/(p[b]-p[b+1]) if p[b]!=p[b+1] else b
            ws.append(xr-xl)
        ws=np.array(ws)
        if len(ws)==0: out.append(None); continue
        # central rows: top 50% widest rows -> median
        k=max(3,len(ws)//2)
        w=float(np.median(np.sort(ws)[-k:])); wmax=float(np.sort(ws)[-2]) if len(ws)>2 else float(ws.max())
        # vertical extent at half max along column through centre (mean of 5 columns)
        col=g[top-15:bot+16,cx-2:cx+3].mean(1); bgc=np.median(np.r_[col[:6],col[-6:]]); pkc=np.percentile(col,95); hc=bgc+0.5*(pkc-bgc)
        idx=np.nonzero(col>hc)[0]; hv=float(idx[-1]-idx[0]+1) if len(idx) else np.nan
        out.append(dict(w=round(w,2),wmax=round(wmax,2),hv=hv))
    res[V]=out
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/width.json','w'))
for i in range(49):
    print(i, '  '.join('none' if res[V][i] is None else f"w={res[V][i]['w']:5.2f} wmax={res[V][i]['wmax']:5.2f} hv={res[V][i]['hv']:4.0f}" for V in res))
