import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0037_segmented.mp4')
rows=[]
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    g=f.astype(np.float32)
    # non-white mask
    d=255-g.min(axis=2)
    roi=d[600:800, 760:1080]
    m=roi>40
    ys,xs=np.nonzero(m)
    if len(ys):
        # restrict to person component: largest component
        n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
        k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
        x,y,w,h,a=st[k]
        cx,cy=cen[k]
        rows.append((i,x+760,y+600,w,h,a,cx+760,cy+600))
    i+=1
rows=np.array(rows)
np.set_printoptions(suppress=True,linewidth=200)
print(rows[::4])
t=rows[:,0]/24
for col,name in [(6,'cx'),(7,'cy')]:
    p=np.polyfit(t,rows[:,col],1); print(name,'slope px/s',p[0])
top=rows[:,2]; bot=rows[:,2]+rows[:,4]
print('height med',np.median(rows[:,4]),'min',rows[:,4].min(),'max',rows[:,4].max())
print('top slope',np.polyfit(t,top,1)[0],'bot slope',np.polyfit(t,bot,1)[0])
