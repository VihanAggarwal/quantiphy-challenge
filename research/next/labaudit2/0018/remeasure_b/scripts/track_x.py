"""Track free objects in the x (white background) render: non-white components not touching persons."""
import cv2, numpy as np, json
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0018/remeasure_b'
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0018x.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
res={}
for i,f in enumerate(fr):
    d=(255*3-f.astype(int).sum(2))
    m=(d>45).astype(np.uint8)
    m[690:,1020:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    comps=[]
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<40 or a>8000: continue
        ys,xs=np.nonzero(lab==k)
        hs=hsv[ys,xs]
        comps.append(dict(c=[float(xs.mean()),float(ys.mean())],bb=[int(x),int(y),int(x+w-1),int(y+h-1)],a=int(a),
                          hue=float(np.median(hs[:,0])),sat=float(np.median(hs[:,1])),val=float(np.median(hs[:,2]))))
    res[i]=comps
json.dump(res,open(f'{OUT}/xcomps.json','w'))
for i in range(26,49):
    print(i,[(round(c['c'][0]),round(c['c'][1]),c['a'],c['bb'][2]-c['bb'][0]+1,c['bb'][3]-c['bb'][1]+1,int(c['hue']),int(c['sat'])) for c in res[i]])
