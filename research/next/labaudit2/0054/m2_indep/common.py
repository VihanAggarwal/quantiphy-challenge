import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0054%s.mp4'
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0054/m2_indep/'
_cache={}
def frames(v):
    if v in _cache: return _cache[v]
    c=cv2.VideoCapture(V%v); fs=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fs.append(f)
    _cache[v]=fs
    return fs
def sheet(v, idxs, x0,y0,x1,y1, scale=1.0, ncol=5, name='sheet'):
    fs=frames(v); tiles=[]
    for i in idxs:
        t=fs[i][y0:y1,x0:x1].copy()
        t=cv2.resize(t,None,fx=scale,fy=scale)
        cv2.putText(t,str(i),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        tiles.append(t)
    while len(tiles)%ncol: tiles.append(np.zeros_like(tiles[0]))
    rows=[np.hstack(tiles[k:k+ncol]) for k in range(0,len(tiles),ncol)]
    img=np.vstack(rows); p=OUT+'sheets/'+name+'.png'; cv2.imwrite(p,img); return p
