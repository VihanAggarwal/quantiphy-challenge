from load import load
import numpy as np, cv2, json
fr=load(gray=False)
e=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edges.json'))
def peaks(i,rows,x0,win,sign=None):
    f=cv2.GaussianBlur(fr[i].astype(np.float32),(0,0),1.5)
    gx=cv2.Sobel(f,cv2.CV_32F,1,0,ksize=3)
    g=np.abs(gx).sum(2)
    out=[]
    for r in rows:
        p=g[r-2:r+3].mean(0)
        a=int(max(1,x0-win)); b=int(min(1918,x0+win))
        seg=p[a:b]; k=int(np.argmax(seg))
        if k==0 or k==len(seg)-1: continue
        y0,y1,y2=seg[k-1],seg[k],seg[k+1]; d=0.5*(y0-y2)/(y0-2*y1+y2)
        out.append((r,a+k+d,y1))
    return np.array(out)
res={}
for i in range(55,84):
    R=np.array(e[str(i)]['R']); up=R[R[:,0]<880]
    rup=np.median(up[:,1])
    for rows,tag in ((range(560,640,4),'Ltop'),(range(660,860,4),'Lmid'),(range(900,1040,4),'Llo')):
        P=peaks(i,rows,rup-417,18)
        if len(P)==0: continue
        res.setdefault(i,{})[tag]=P.tolist()
    s=res[i]
    print(i,'Rup %.2f'%rup,' '.join('%s %.2f(mad %.2f,str %.0f)'%(k,np.median(np.array(v)[:,1]),np.median(abs(np.array(v)[:,1]-np.median(np.array(v)[:,1]))),np.median(np.array(v)[:,2])) for k,v in s.items()))
json.dump(res,open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edgesL.json','w'))
