import cv2, numpy as np
W='research/next/audit3/internet_10/remeasure/'
sh=np.loadtxt(W+'shifts_clean.txt')
dx=(sh[:,0]+sh[:,2])/2; dy=(sh[:,1]+sh[:,3])/2
t=np.loadtxt(W+'rider_track.txt')
good=(t[:,0]>=12)&(t[:,0]<=91)
p=np.polyfit(t[good,0],t[good,6],1); print('shirt fit 12-91 slope px/frame',p)
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
frames=[]
for i in range(94):
    ok,f=c.read()
    M=np.float32([[1,0,-dx[i]],[0,1,-dy[i]]])
    frames.append(cv2.warpAffine(f[700:1200],M,(3840,500),borderMode=cv2.BORDER_REPLICATE) if False else None)
c.release()
# template matching route: template = rider body from frame 48 (stabilised coordinates)
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
st=[]
for i in range(94):
    ok,f=c.read()
    M=np.float32([[1,0,-dx[i]],[0,1,-dy[i]]])
    g=cv2.warpAffine(f,M,(3840,2160),borderMode=cv2.BORDER_REPLICATE)[780:1160]
    st.append(g)
st=np.array(st)
bg=np.median(st,axis=0).astype(np.float32)
res=[]
for i in range(94):
    pred=np.polyval(p,i)
    d=np.abs(st[i].astype(np.float32)-bg).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    x0=int(max(0,pred-260)); x1=int(min(3840,pred+260))
    sub=m[:,x0:x1]
    ys,xs=np.nonzero(sub)
    if len(xs)==0: res.append([i,np.nan]*1+[np.nan]*5); continue
    xs=xs+x0
    # white shirt pixels
    img=st[i][:, x0:x1].astype(int)
    wm=(img.min(2)>170)&(sub>0)
    wy,wx=np.nonzero(wm)
    # silhouette extents (rows 0..380 -> 780..1160)
    left=np.percentile(xs,0.5); right=np.percentile(xs,99.5)
    top=ys.min()+780; bot=ys.max()+780
    res.append([i,wx.mean()+x0 if len(wx) else np.nan,left,right,top,bot,len(wx)])
res=np.array(res,float)
np.savetxt(W+'rider_track2.txt',res,fmt='%.1f',header='frame shirt_x sil_left sil_right sil_top sil_bot nshirt (stabilised)')
fr=res[:,0]
for k,name in ((1,'shirt'),(2,'left'),(3,'right')):
    ok=np.isfinite(res[:,k])
    pp=np.polyfit(fr[ok],res[ok,k],1); r=res[ok,k]-np.polyval(pp,fr[ok])
    print(name,'slope %.3f px/frame  resid rms %.2f'%(pp[0],r.std()))
    print('  net (x93-x0)/93 = %.3f'%((res[93,k]-res[0,k])/93))
print(res[::8].round(1))
