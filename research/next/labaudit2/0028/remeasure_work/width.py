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
F={v:frames(v) for v in ['captured_0028','captured_0028s','captured_0028x']}
def halfwidth(prof):
    # prof: 1D array; background = median of ends; peak=max; FWHM crossing with interpolation
    bg=np.median(np.r_[prof[:4],prof[-4:]]); pk=np.percentile(prof,95)
    if pk-bg<20: return np.nan
    h=(bg+pk)/2
    above=np.nonzero(prof>h)[0]
    if len(above)<3: return np.nan
    l=above[0]; r=above[-1]
    # interpolate
    xl=l-1+(h-prof[l-1])/(prof[l]-prof[l-1])
    xr=r+(prof[r]-h)/(prof[r]-prof[r+1])
    return xr-xl
out={}
for i in range(18,47):
    cx,cy=tr[i]['cx'],tr[i]['cy']
    row=[]
    for v in F:
        g=cv2.cvtColor(F[v][i],cv2.COLOR_BGR2GRAY).astype(float)
        # horizontal widths over rows near center (+-3), take max
        ws=[]
        for dy in range(-4,5):
            y=int(round(cy))+dy
            prof=g[y,int(cx)-20:int(cx)+21]
            ws.append(halfwidth(prof))
        row.append(np.nanmax(ws) if not np.all(np.isnan(ws)) else np.nan)
    out[i]=row
    print(i, ' '.join(f'{w:6.2f}' for w in row), f' Z(x)={711*0.04/row[2]:.3f}')
