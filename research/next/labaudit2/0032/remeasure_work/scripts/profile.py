import cv2, numpy as np, sys
src=sys.argv[1]
cap=cv2.VideoCapture(src); fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
# initial centres from colour blob
def blob(f):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
    roi=np.zeros(hsv.shape[:2],bool); roi[380:520,450:1000]=True
    m=((hsv[...,1]<60)&(hsv[...,2]>170)&roi).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); return cen[k]
for i in range(36,49):
    f=fr[i]; cx,cy=blob(f)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(float)
    # whiteness: V high and S low
    W=(hsv[...,2]/255.0)*(1-hsv[...,1]/255.0)
    x0,y0=int(round(cx)),int(round(cy))
    # vertical profile: average over central 5 columns
    vp=W[y0-25:y0+26, x0-2:x0+3].mean(1)
    hp=W[y0-3:y0+4, x0-30:x0+31].mean(0)
    def edges(p,off):
        mx=p.max(); mn=np.median(np.r_[p[:5],p[-5:]]); th=(mx+mn)/2
        idx=np.where(p>th)[0]
        a=idx[0]; b=idx[-1]
        # subpixel
        lo=a-1+(th-p[a-1])/(p[a]-p[a-1]); hi=b+(p[b]-th)/(p[b]-p[b+1])
        return lo+off, hi+off
    t,bm=edges(vp,y0-25); l,r=edges(hp,x0-30)
    print(i, 'blob=(%.1f,%.1f)'%(cx,cy), 'top=%.1f bot=%.1f H=%.1f'%(t,bm,bm-t), 'left=%.1f right=%.1f W=%.1f'%(l,r,r-l), 'ctr=(%.1f,%.1f)'%((l+r)/2,(t+bm)/2))
