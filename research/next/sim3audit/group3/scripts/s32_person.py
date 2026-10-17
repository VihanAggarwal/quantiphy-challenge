import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0032_segmented.mp4')
i=0; rows=[]
while True:
    ok,f=c.read()
    if not ok: break
    g=f.astype(int)
    m=((255*3-g.sum(2))>60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=max(range(1,n),key=lambda k:st[k,4])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    # feet: lowest rows; per-column bottom
    bot=ys.max(); top=ys.min()
    # head top: topmost row among pixels near column median of the torso
    rows.append(dict(f=i,x=int(x),y=int(y),w=int(w),h=int(h),a=int(a),top=int(top),bot=int(bot),cx=float(xs.mean()),cy=float(ys.mean())))
    i+=1
json.dump(rows,open('/home/user/quantiphy-challenge/research/next/sim3audit/group3/s32_person.json','w'))
for r in rows: print(r['f'],r['x'],r['w'],r['top'],r['bot'],r['bot']-r['top'],r['a'],round(r['cx'],1),round(r['cy'],1))
