import cv2,numpy as np,json
W=json.load(open('wrow.json'))
out={}
for i in range(36,49):
    img=cv2.imread('frames/f%02d.png'%i)
    L=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,0].astype(float)
    xc,yc,R=W[str(i)][1][:3]
    tops=[]
    for dx in range(-3,4):
        X=int(round(xc))+dx
        col=L[:,X]
        Y0=int(round(yc-R))
        seg=col[Y0-8:Y0+6]
        bg=np.median(col[Y0-12:Y0-5]); pk=col[Y0:Y0+5].max()
        thr=(bg+pk)/2
        idx=np.where(seg>thr)[0]
        k=idx[0]
        yt=Y0-8+k-1+(thr-seg[k-1])/(seg[k]-seg[k-1])
        tops.append(yt)
    tops=np.array(tops)
    # correct for column offset from centre: circle top at column dx is yc - sqrt(R^2-dx^2); small
    corr=np.array([R-np.sqrt(R*R-(dx+round(xc)-xc)**2) for dx in range(-3,4)])
    ytop=np.mean(tops-corr)
    out[i]=dict(ytop=ytop,spread=float(np.std(tops-corr)),xc=xc,d=2*R)
    print(i,'ytop=%.2f sd=%.2f  xc=%.2f d_row=%.2f'%(ytop,np.std(tops-corr),xc,2*R), np.round(tops,2))
json.dump(out,open('wtop.json','w'))
