import numpy as np, cv2, json
from load import frames
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
clip='simulation_0010'
a=frames(D+clip+'.mp4',gray=True)
bg=np.median(a.astype(np.int16),axis=0)
tr=json.load(open(f'../{clip}_bird.json'))
segtr=json.load(open('../simulation_0010_segmented_bird.json'))
res=[]
for i in range(0,58):
    t=segtr[i]
    x1=t['x1']; cy=int(t['cy'])
    f=a[i].astype(np.int16)
    m=(np.abs(f-bg)>40)
    # head template: front 55 px of the bird, rows cy-60..cy+60
    X0=x1-55; X1=x1+5; Y0=cy-60; Y1=cy+60
    tmpl=a[i][Y0:Y1,X0:X1]; tm=(m[Y0:Y1,X0:X1]).astype(np.uint8)
    if tm.sum()<200: res.append(None); continue
    sw=60
    srch=a[i+1][Y0-30:Y1+30, X0-10:X1+sw]
    r=cv2.matchTemplate(srch,tmpl,cv2.TM_SQDIFF,mask=tm)
    mn,mx,mnl,mxl=cv2.minMaxLoc(r)
    dx=mnl[0]-10; dy=mnl[1]-30
    res.append((i,dx,dy))
    print(i,dx,dy,int(mn/ max(tm.sum(),1)))
json.dump(res,open('../bird_headflow.json','w'))
