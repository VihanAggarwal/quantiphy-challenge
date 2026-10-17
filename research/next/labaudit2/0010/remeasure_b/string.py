import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0010s.mp4')
B=json.load(open('ballfit.json'))['captured_0010s']
j=0; res=[]
while True:
    ok,f=c.read()
    if not ok: break
    g=f.astype(int)
    # non-green: green channel not dominant
    ng=((g[...,1]-np.maximum(g[...,0],g[...,2]))<25)
    ng[:150]=False; ng[int(B[j]['v'])-20:]=False
    ys,xs=np.nonzero(ng[:, 560:760]); xs=xs+560
    if len(ys):
        top=ys.min(); sel=ys<=top+3
        res.append((j,int(top),float(xs[sel].mean()),len(ys)))
    else: res.append((j,None,None,0))
    j+=1
for r in res: print(r)
