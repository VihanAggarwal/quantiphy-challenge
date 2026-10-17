from load import load
import numpy as np, cv2, json
fr=load(gray=False)
b=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/bands.json'))
for i in range(61,80):
    l,r=b[str(i)]['lo']; c=(l+r)/2
    f=cv2.GaussianBlur(fr[i].astype(np.float32),(0,0),1.2)
    gy=np.abs(cv2.Sobel(f,cv2.CV_32F,0,1,ksize=3)).sum(2)
    res=[]
    for dx in (-60,-30,0,30,60):
        x=int(round(c+dx))
        col=gy[:,x-3:x+4].mean(1)
        def pk(a,bnd):
            seg=col[a:bnd]; k=int(np.argmax(seg)); 
            if 0<k<len(seg)-1:
                y0,y1,y2=seg[k-1],seg[k],seg[k+1]; d=0.5*(y0-y2)/(y0-2*y1+y2)
            else: d=0
            return a+k+d, seg[k]
        t=pk(470,560); bt=pk(1030,1078)
        res.append((t[0],bt[0],t[1],bt[1]))
    res=np.array(res)
    print(i,'c %.1f top %s bot %s H %.2f'%(c,np.round(res[:,0],1),np.round(res[:,1],1),np.median(res[:,1]-res[:,0])), 'str',np.round(res[:,2]).astype(int),np.round(res[:,3]).astype(int))
