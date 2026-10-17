# Track soccer ball (sb) and basketball (bb) centres + equivalent diameters in ax render (green screen).
import cv2, numpy as np, json
V='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0035ax.mp4'
c=cv2.VideoCapture(V); frames=[]
while True:
    ok,f=c.read()
    if not ok: break
    frames.append(f)
def gmask(f):
    b,g,r=[f[...,k].astype(int) for k in range(3)]
    # "greenness": g - max(r,b)
    return g-np.maximum(r,b)
res={}
prev={'sb':None,'bb':None}
for i,f in enumerate(frames):
    gn=gmask(f)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    for thr in (100,):
        fg=(gn<thr).astype(np.uint8)
        fg[690:,1030:]=0  # watermark
        n,lab,st,cen=cv2.connectedComponentsWithStats(fg)
        orange=((hsv[...,0]>=0)&(hsv[...,0]<=22)&(hsv[...,1]>110)&(hsv[...,2]>60))
        row={}
        for k in range(1,n):
            x,y,w,h,a=st[k]
            if a<800 or a>9000 or w>130 or h>130: continue
            m=lab==k
            ofr=orange[m].mean()
            ys,xs=np.nonzero(m)
            # soft-weighted centroid using alpha from greenness
            sub=gn[y:y+h,x:x+w].astype(float)
            alpha=np.clip((150-sub)/100,0,1)
            yy,xx=np.mgrid[y:y+h,x:x+w]
            cxw=(alpha*xx).sum()/alpha.sum(); cyw=(alpha*yy).sum()/alpha.sum()
            cnt,_=cv2.findContours(m[y:y+h,x:x+w].astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            cnt=max(cnt,key=cv2.contourArea)
            (ex,ey),er=cv2.minEnclosingCircle(cnt)
            if len(cnt)>=5:
                el=cv2.fitEllipse(cnt)
            else: el=((0,0),(0,0),0)
            d=dict(cx=float(xs.mean()),cy=float(ys.mean()),cxw=float(cxw),cyw=float(cyw),area=int(a),deq=float(2*np.sqrt(a/np.pi)),
                   dsoft=float(2*np.sqrt(alpha.sum()/np.pi)),w=int(w),h=int(h),ecx=float(ex+x),ecy=float(ey+y),er=float(er),
                   elcx=float(el[0][0]+x),elcy=float(el[0][1]+y),elax=[float(el[1][0]),float(el[1][1])],orange=float(ofr))
            key='bb' if ofr>0.5 else 'sb'
            if key in row and row[key]['area']>a: continue
            row[key]=d
        res[i]=row
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/track_ax.json','w'),indent=0)
for i in range(len(frames)):
    s=res[i].get('sb'); b=res[i].get('bb')
    fs=lambda d: '%7.2f %7.2f deq%5.1f ds%5.1f el%5.1f/%5.1f' %(d['cxw'],d['cyw'],d['deq'],d['dsoft'],*d['elax']) if d else '-'
    print(i,'SB',fs(s),' | BB',fs(b))
