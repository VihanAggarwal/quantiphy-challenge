import cv2, numpy as np
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
med=cv2.imread(d+'median_x.png').astype(float)
m=(med.max(axis=2)>35)
H,W=m.shape
# back edge: topmost mask pixel per column within table region rows 415-445
bx=[];by=[]
for x in range(585,835):
    if 630<=x<=665 or 750<=x<=775: continue
    col=m[410:450,x]
    if col.any():
        y=410+np.argmax(col); bx.append(x); by.append(y)
bx=np.array(bx);by=np.array(by)
pb=np.polyfit(bx,by,1); print('back', pb, 'resid', np.std(by-np.polyval(pb,bx)))
# left side edge: leftmost per row
lx=[];ly=[]
for y in range(432,478):
    row=m[y,400:700]
    if row.any(): lx.append(400+np.argmax(row)); ly.append(y)
lx=np.array(lx);ly=np.array(ly)
pl=np.polyfit(ly,lx,1); print('left', pl, np.std(lx-np.polyval(pl,ly)))
rx=[];ry=[]
for y in range(434,488):
    row=m[y,700:1050]
    if row.any(): rx.append(700+len(row)-1-np.argmax(row[::-1])); ry.append(y)
rx=np.array(rx);ry=np.array(ry)
pr=np.polyfit(ry,rx,1); print('right', pr, np.std(rx-np.polyval(pr,ry)))
# print profiles to find kinks
for y in range(470,510,2):
    row=m[y]
    xs=np.where(row[300:1100])[0]
    print(y, 300+xs.min() if len(xs) else None, 300+xs.max() if len(xs) else None)
# front edge: vertical gradient in gray
g=cv2.cvtColor(med.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(float)
g=cv2.GaussianBlur(g,(3,3),0)
gy=np.diff(g,axis=0)
fx=[];fy=[]
for x in range(500,940,5):
    seg=gy[465:505,x]
    y=465+np.argmin(seg)  # bright top -> darker face? check sign
    y2=465+np.argmax(seg)
    fx.append(x); fy.append((y,y2,seg.min(),seg.max()))
for a,b in zip(fx,fy): print(a,b)
np.save(d+'edges.npy',dict(pb=pb,pl=pl,pr=pr))
