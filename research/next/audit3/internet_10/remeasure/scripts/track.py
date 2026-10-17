import cv2, numpy as np
W='research/next/audit3/internet_10/remeasure/'
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
Y0,Y1=700,1180
band=[];shifts=[]
ref=None
i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    rois={'Lh':(slice(760,1060),slice(50,900)),'Rh':(slice(780,1080),slice(3150,3750)),'bld':(slice(100,700),slice(100,1800))}
    if ref is None:
        ref={k:g[v] for k,v in rois.items()}; win={k:cv2.createHanningWindow(ref[k].shape[::-1],cv2.CV_32F) for k in rois}
    row=[]
    for k,v in rois.items():
        (dx,dy),r=cv2.phaseCorrelate(ref[k],g[v],win[k]); row+=[dx,dy]
    shifts.append(row)
    band.append(f[Y0-60:Y1+60].copy())
    i+=1
shifts=np.array(shifts)
np.savetxt(W+'shifts_clean.txt',shifts,fmt='%.2f',header='Lh_dx Lh_dy Rh_dx Rh_dy bld_dx bld_dy')
print(shifts[::10].round(1)); print(shifts[-1].round(1))
# stabilise band to frame0 using mean of Lh and Rh shifts (at rider depth)
dx=(shifts[:,0]+shifts[:,2])/2; dy=(shifts[:,1]+shifts[:,3])/2
st=[]
for k,b in enumerate(band):
    M=np.float32([[1,0,-dx[k]],[0,1,-dy[k]]])
    st.append(cv2.warpAffine(b,M,(b.shape[1],b.shape[0]),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)[60:-60])
st=np.array(st)
bg=np.median(st,axis=0).astype(np.float32)
cv2.imwrite(W+'bg_band.jpg',cv2.resize(bg,(1920,240)).astype(np.uint8))
out=[]
for k in range(len(st)):
    d=np.abs(st[k].astype(np.float32)-bg).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    n,lab,stats,cent=cv2.connectedComponentsWithStats(m)
    if n<2: out.append([k]+[np.nan]*7); continue
    j=1+np.argmax(stats[1:,4])
    x,y,w,h,a=stats[j]
    # white shirt pixels inside component
    sub=st[k][y:y+h,x:x+w].astype(int)
    wm=(sub.min(2)>170)&(lab[y:y+h,x:x+w]==j)
    ys,xs=np.nonzero(wm)
    sx=xs.mean()+x if len(xs) else np.nan
    out.append([k,x,y+Y0,w,h,a,sx,cent[j][0]])
out=np.array(out,float)
np.savetxt(W+'rider_track.txt',out,fmt='%.1f',header='frame bx by(full) bw bh area shirt_x cent_x  (stabilised to frame0, rider-depth shift)')
for r in out[::6]: print(r.round(1))
