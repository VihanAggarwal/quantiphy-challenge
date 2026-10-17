# A2 (frontal) view: letter x-extent vs table x-extent at the same image row.
import cv2, numpy as np, sys
def load(vid, fi=0):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
    fr=None
    for i in range(fi+1):
        ok,fr=cap.read()
    return fr
def fitline(ys,xs):
    A=np.vstack([ys,np.ones_like(ys)]).T
    p,res,_,_=np.linalg.lstsq(A,xs,rcond=None)
    r=xs-A@p
    # one robust pass
    m=np.abs(r)<max(1.5,3*np.std(r))
    p,_,_,_=np.linalg.lstsq(A[m],xs[m],rcond=None)
    return p, np.std((xs-A@p)[m]), m.sum()
for vid in sys.argv[1:]:
    im=load(vid,0).astype(np.float32)
    g=cv2.GaussianBlur(cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0)
    b,gg,r=[im[:,:,k] for k in range(3)]
    # background is blue-ish: b - r large; table is brown/dark: b-r small
    bluish = (b - r)
    ysL=[];xsL=[];ysR=[];xsR=[]
    for y in range(965,1076):
        row=cv2.GaussianBlur(bluish,(5,5),0)[y]
        # left: scan from left, background has bluish>T; find first x where bluish drops below mid
        bg=np.median(row[0:15]); 
        # find left transition in x 0..400
        seg=row[0:420]
        tab=np.median(row[430:470]) if False else None
        # use gradient of bluish: largest negative gradient
        d=np.diff(seg)
        x=np.argmin(d)
        # subpixel: half level crossing
        lo=seg[max(x-8,0)]; hi=seg[min(x+8,len(seg)-1)]; mid=(lo+hi)/2
        xs=np.arange(max(x-8,0),min(x+8,len(seg)-1))
        k=None
        for j in range(len(xs)-1):
            a,c=seg[xs[j]],seg[xs[j+1]]
            if (a-mid)*(c-mid)<=0 and a!=c:
                k=xs[j]+(mid-a)/(c-a); break
        if k is not None: ysL.append(y); xsL.append(k)
        seg=row[1650:2124]
        d=np.diff(seg); x=np.argmax(d)
        lo=seg[max(x-8,0)]; hi=seg[min(x+8,len(seg)-1)]; mid=(lo+hi)/2
        xs=np.arange(max(x-8,0),min(x+8,len(seg)-1)); k=None
        for j in range(len(xs)-1):
            a,c=seg[xs[j]],seg[xs[j+1]]
            if (a-mid)*(c-mid)<=0 and a!=c:
                k=xs[j]+(mid-a)/(c-a); break
        if k is not None: ysR.append(y); xsR.append(1650+k)
    pL,sL,nL=fitline(np.array(ysL,float),np.array(xsL,float))
    pR,sR,nR=fitline(np.array(ysR,float),np.array(xsR,float))
    # VP
    # x = a y + c ; intersection
    yv=(pR[1]-pL[1])/(pL[0]-pR[0]); xv=pL[0]*yv+pL[1]
    print(vid,'left edge x=%.4f*y+%.1f rms %.2f n=%d'%(pL[0],pL[1],sL,nL),' right x=%.4f*y+%.1f rms %.2f n=%d'%(pR[0],pR[1],sR,nR))
    print('   VP (%.1f, %.1f)'%(xv,yv), ' W(y)= %.4f*(y-%.1f)'%(pR[0]-pL[0], yv))
    np.save(f'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/{vid}_edges.npy',np.array([pL,pR]))
