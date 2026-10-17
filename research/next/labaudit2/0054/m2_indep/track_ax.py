from common import *
import numpy as np, cv2, json
fs=frames('ax')
res={}
for i,f in enumerate(fs):
    b,g,r=[f[:,:,k].astype(int) for k in range(3)]
    bg=(g>180)&(r<120)&(b<120)
    fg=(~bg).astype(np.uint8)
    fg[690:,1020:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg,8)
    out=[]
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if 30<a<4000 and max(w,h)<150:
            m=lab==k
            col=f[m].mean(0)
            out.append(dict(k=int(k),x=float(cen[k][0]),y=float(cen[k][1]),w=int(w),h=int(h),a=int(a),bgr=[round(float(c)) for c in col]))
    res[i]=out
    print(i,[(round(o['x']),round(o['y']),o['w'],o['h'],o['a'],o['bgr']) for o in out])
json.dump(res,open(OUT+'ax_blobs.json','w'))
