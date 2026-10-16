import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
res={}
for i in range(49):
    im=cv2.imread(d+f'frames/0020x_f{i:02d}.png').astype(int)
    b,g,r=im[...,0],im[...,1],im[...,2]
    green=(g>150)&(r<120)&(b<120)
    fg=(~green).astype(np.uint8)
    fg[690:,1000:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg)
    hsv=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(int)
    comps=[]
    for k in range(1,n):
        if st[k,4]<60: continue
        m=lab==k
        hh=hsv[...,0][m]; ss=hsv[...,1][m]; vv=hsv[...,2][m]
        yel=np.mean((hh>=18)&(hh<=40)&(ss>70)); wht=np.mean((ss<50)&(vv>170))
        comps.append(dict(area=int(st[k,4]),bbox=[int(x) for x in st[k,:4]],c=[round(float(x),1) for x in cen[k]],yel=round(float(yel),2),wht=round(float(wht),2)))
    comps.sort(key=lambda c:-c['area'])
    res[i]=comps
    print(i,[ (c['area'],c['bbox'],c['c'],c['yel'],c['wht']) for c in comps[:5]])
json.dump(res,open(d+'xseg.json','w'))
