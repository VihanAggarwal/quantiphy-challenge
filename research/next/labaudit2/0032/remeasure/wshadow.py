import cv2,numpy as np,json
Ww=json.load(open('wrow.json'))
out={}
for i in range(33,49):
    img=cv2.imread('frames/f%02d.png'%i)
    L=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,0].astype(float)
    if str(i) in Ww: xc,yc,R=Ww[str(i)][1][:3]
    else: continue
    ys=[]
    for dx in range(-4,5):
        X=int(round(xc))+dx
        col=cv2.GaussianBlur(L[:,X-1:X+2],(1,3),0).mean(1) if False else L[:,X-1:X+2].mean(1)
        lo=int(yc+0.6*R); hi=int(yc+R+8)
        seg=col[lo:hi]; k=np.argmin(seg)
        if 0<k<len(seg)-1:
            a,b,c=seg[k-1],seg[k],seg[k+1]; off=0.5*(a-c)/(a-2*b+c)
            ys.append(lo+k+off)
    ys=np.array(ys)
    out[i]=dict(ysh=float(np.median(ys)),sd=float(ys.std()),yc=yc,R=R)
    print(i,'shadow y=%.2f sd=%.2f   yc_row=%.2f  ysh-yc=%.2f R=%.2f'%(np.median(ys),ys.std(),yc,np.median(ys)-yc,R))
json.dump(out,open('wshadow.json','w'))
