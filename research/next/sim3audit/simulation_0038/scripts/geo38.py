import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0038_segmented.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
orig=[int(np.floor(24*k/25)) for k in range(len(fr))]
# person head-top track: topmost non-white pixel in person region (exclude shadow which is to the right/up)
heads=[];feet=[]
for k,f in enumerate(fr):
    if k in (1,26,51): continue
    g=f.astype(np.int16); m=((255-g.min(axis=2))>60)
    sub=m[740:940,460:620]
    n,lab,st,cen=cv2.connectedComponentsWithStats(sub.astype(np.uint8))
    kk=1+np.argmax(st[1:,4]); comp=(lab==kk)
    ys,xs=np.nonzero(comp)
    # person = columns left part: take pixels with x < xs.min()+16
    sel=xs< xs.min()+16
    y_top=ys[sel].min(); 
    # head x: mean x of pixels within 3 rows of top
    hx=xs[sel][ys[sel]<=y_top+3].mean()
    y_bot=ys[sel].max()
    heads.append((orig[k],hx+460,y_top+740)); feet.append((orig[k],y_bot+740))
H=np.array(heads); F=np.array(feet)
t=H[:,0]/24
px=np.polyfit(t,H[:,1],1); py=np.polyfit(t,H[:,2],1)
print('head vel px/s', px[0], py[0], 'pos@t1', np.polyval(px,1), np.polyval(py,1))
print('feet y slope', np.polyfit(t,F[:,1],1)[0])
h=F[:,1]-H[:,2]
print('proj height med', np.median(h), 'p25 p75', np.percentile(h,[25,75]), 'max', h.max())
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/h38.npy', np.c_[H,F[:,1]])
