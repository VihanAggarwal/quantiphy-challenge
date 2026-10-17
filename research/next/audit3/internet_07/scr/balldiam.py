import cv2, numpy as np
W='/home/user/quantiphy-challenge/research/next/audit3/internet_07/'
B={int(r[0]):(r[1],r[2]) for r in np.loadtxt(W+'ball64.txt')}
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0064.mp4'); f=0
res=[]
while True:
    ok,im=cap.read()
    if not ok: break
    if f in B:
        cx,cy=B[f]; x0=int(cx-80); y0=int(cy-80)
        c=im[max(0,y0):y0+160,max(0,x0):x0+160].astype(np.float32)
        b,g,r=c[:,:,0],c[:,:,1],c[:,:,2]
        red=r-(g+b)/2
        inner=np.median(red[60:100,60:100]) if red.shape[0]>=100 and red.shape[1]>=100 else np.nan
        bgv=np.median(np.r_[red[:10].ravel(),red[-10:].ravel()])
        thr=(inner+bgv)/2
        m=(red>thr)
        # vertical extent through center column band, horizontal extent through center row band (subpixel via profile)
        colp=red[:,70:90].mean(1); rowp=red[70:90,:].mean(0)
        def extent(p):
            above=np.where(p>thr)[0]
            if len(above)<5: return np.nan
            i0,i1=above[0],above[-1]
            a=i0-1+(thr-p[i0-1])/(p[i0]-p[i0-1]) if i0>0 else i0
            bb=i1+(p[i1]-thr)/(p[i1]-p[i1+1]) if i1+1<len(p) else i1
            return bb-a
        area=m.sum(); deq=2*np.sqrt(area/np.pi)
        res.append((f,extent(colp),extent(rowp),deq,inner,bgv))
    f+=1
res=np.array(res)
for r in res:
    if r[0]%3==0: print('%d vert %.1f horiz %.1f d_eq %.1f (inner %.0f bg %.0f)'%tuple(r))
np.savetxt(W+'balldiam64.txt',res,fmt='%.2f')
