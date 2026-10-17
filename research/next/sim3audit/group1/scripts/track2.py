import cv2, numpy as np, json, sys
v = sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg = cv2.imread('scripts/bg_final.png').astype(np.float32)
yh=540.4
out=[]
for i,f in enumerate(fr):
    d = np.abs(f.astype(np.float32)-bg).max(2)
    m = (d>30).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    n,lab,st,cen = cv2.connectedComponentsWithStats(m)
    k = 1+np.argmax(st[1:,4]); x,y,w,h,a = st[k]
    man = lab==k
    ys,xs = np.nonzero(man)
    rows = np.bincount(ys, minlength=f.shape[0]); top = np.nonzero(rows>=3)[0].min()
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    dark = man & (hsv[...,2]<40)
    dys,dxs = np.nonzero(dark)
    drows = np.bincount(dys, minlength=f.shape[0]); low = np.nonzero(drows>=2)[0].max()
    # torso x: mean x of mask rows between top+15% and top+45% of (low-top)
    hgt = low-top
    sel = (ys>top+0.15*hgt)&(ys<top+0.45*hgt)
    xt = xs[sel].mean()
    xlow = dxs[dys>=low-2].mean()
    out.append(dict(i=i, top=int(top), low=int(low), xt=float(xt), xlow=float(xlow), r=(low-top)/(low-yh)))
    if i%10==0: cv2.imwrite(f'frames/m2_{v[-4:]}_{i:03d}.png', (man*255).astype(np.uint8)[300:1080, 400:1100])
json.dump(out, open(f'scripts/{v}_t2.json','w'))
for o in out: print(o['i'], o['top'], o['low'], round(o['xt'],1), round(o['xlow'],1), round(o['r'],4), round(1e3/(o['low']-yh),4))
