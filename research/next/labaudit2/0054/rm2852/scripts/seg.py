import cv2, numpy as np, json, sys
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
ax=np.load(S+'ax.npy')
out={}
for k in range(len(ax)):
    f=ax[k].astype(np.int16)
    d=np.sqrt(((f-np.array([0,252,0]))**2).sum(-1))
    fg=(d>60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg,8)
    comps=[]
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if a<15 or a>3000: continue
        m=lab==i
        col=ax[k][m].mean(0)
        hsv=cv2.cvtColor(ax[k][m].reshape(-1,1,3),cv2.COLOR_BGR2HSV).reshape(-1,3).mean(0)
        comps.append(dict(c=[float(cen[i][0]),float(cen[i][1])],bbox=[int(x),int(y),int(w),int(h)],area=int(a),bgr=[round(float(v)) for v in col],hsv=[round(float(v)) for v in hsv]))
    out[k]=comps
    print(k,[ (round(c['c'][0]),round(c['c'][1]),c['area'],c['bbox'][2:],c['bgr']) for c in comps])
json.dump(out,open(S+'comps_ax.json','w'))
