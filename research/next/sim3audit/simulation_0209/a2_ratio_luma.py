# Precise A2 ratio: letter x-extent / table silhouette width at the same image row (luma edges, subpixel).
import cv2, numpy as np, sys
def load(vid):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4'); ok,fr=cap.read(); return fr
def cross(prof, thr, start, step):
    # first crossing of thr walking from start in direction step; return subpixel position
    i=start
    while 0<i<len(prof)-1:
        a,b=prof[i],prof[i+step]
        if (a-thr)*(b-thr)<=0 and a!=b: return i+step*(thr-a)/(b-a)
        i+=step
    return np.nan
for vid in sys.argv[1:]:
    im=load(vid); Y=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    # table silhouette edges via luma (table darker than wall at sides?) -> use colour distance to wall instead
    lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(np.float32)
    wallL=np.median(lab[970:1075,0:10].reshape(-1,3),axis=0); wallR=np.median(lab[970:1075,2114:2124].reshape(-1,3),axis=0)
    ys=np.arange(966,1076); xl=[];xr=[]
    for y in ys:
        dl=np.linalg.norm(lab[y,0:500]-wallL,axis=1); dr=np.linalg.norm(lab[y,1600:2124]-wallR,axis=1)
        dl=np.convolve(dl,np.ones(3)/3,'same'); dr=np.convolve(dr,np.ones(3)/3,'same')
        tl=(np.median(dl[:10])+np.median(dl[-60:]))/2; tr=(np.median(dr[-10:])+np.median(dr[:60]))/2
        xl.append(cross(dl,tl,2,1)); xr.append(1600+cross(dr,tr,len(dr)-3,-1))
    xl=np.array(xl); xr=np.array(xr)
    def rfit(y,x):
        m=np.isfinite(x)
        for it in range(3):
            p=np.polyfit(y[m],x[m],1); r=x-np.polyval(p,y); s=np.std(r[m]); m=m&(np.abs(r)<max(1.0,2.5*s))
        return p,np.std(r[m]),m.sum()
    pl,sl,nl=rfit(ys,xl); pr,sr,nr=rfit(ys,xr)
    yv=(pr[1]-pl[1])/(pl[0]-pr[0]); xv=np.polyval(pl,yv)
    W=lambda y: np.polyval(pr,y)-np.polyval(pl,y)
    print(vid,'left rms %.2f n=%d  right rms %.2f n=%d  VP (%.1f,%.1f)  W(1000)=%.1f'%(sl,nl,sr,nr,xv,yv,W(1000)))
    # letter: luma profile across rows inside the paper near its front edge
    for y in range(986,1001):
        prof=Y[y,1150:1430]; 
        paper=np.percentile(prof,90); table=np.median(Y[y,1100:1150])
        thr=(paper+table)/2
        a=cross(prof,thr,0,1); b=cross(prof,thr,len(prof)-1,-1)
        a+=1150; b+=1150
        print('   row %d: letter %.1f..%.1f = %.1f px; W=%.1f ratio %.4f -> L(2.44) %.3f'%(y,a,b,b-a,W(y),(b-a)/W(y),2.44*(b-a)/W(y)))
