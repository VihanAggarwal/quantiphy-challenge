import cv2, numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
ok,f=c.read()
g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float)
rows=[];wid=[];cen=[]
import sys
lo,hi=int(sys.argv[1]),int(sys.argv[2])
for y in range(lo,hi,5):
    if 1300<y<1560: continue  # skip circle area
    prof=g[y-2:y+3,1700:2000].mean(0)
    # half-max width around the peak
    k=np.argmax(np.convolve(prof,np.ones(9)/9,'same'))
    pk=prof[max(0,k-15):k+16].max(); bgl=np.median(prof)
    half=(pk+bgl)/2
    # left crossing
    i=k
    while i>0 and prof[i]>half: i-=1
    xl=i+(half-prof[i])/(prof[i+1]-prof[i])
    j=k
    while j<len(prof)-1 and prof[j]>half: j+=1
    xr=j-1+(prof[j-1]-half)/(prof[j-1]-prof[j])
    rows.append(y); wid.append(xr-xl); cen.append((xl+xr)/2+1700)
rows=np.array(rows);wid=np.array(wid);cen=np.array(cen)
p=np.polyfit(rows,wid,1)
r=wid-np.polyval(p,rows)
ok=np.abs(r)<3*r.std()
p=np.polyfit(rows[ok],wid[ok],1)
print('width = %.4f*y + %.2f ; zero at y=%.1f ; resid rms %.2f'%(p[0],p[1],-p[1]/p[0],(wid[ok]-np.polyval(p,rows[ok])).std()))
for y,w,cc in zip(rows[::6],wid[::6],cen[::6]): print(y,round(w,2),round(cc,1))
# blur bias check: subtract a constant k px from width
for b in (-2,-1,1,2):
    q=np.polyfit(rows[ok],wid[ok]+b,1); print('bias %+d px -> horizon %.1f'%(b,-q[1]/q[0]))
