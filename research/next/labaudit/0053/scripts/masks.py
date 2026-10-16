import cv2, numpy as np, json
out={}
for n in range(48):
    im=cv2.imread(f'frames/x_{n:02d}.png').astype(int)
    b,g,r=im[...,0],im[...,1],im[...,2]
    green=(g>200)&(r<80)&(b<80)
    m=(~green).astype(np.uint8)
    m[690:,1000:]=0  # watermark
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    k,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[]
    for i in range(1,k):
        x,y,w,h,a=st[i]
        if a<80: continue
        comps.append(dict(x=int(x),y=int(y),w=int(w),h=int(h),a=int(a),cx=float(cen[i][0]),cy=float(cen[i][1])))
    out[n]=comps
    if n in (0,10,20,34,47): print(n,[(c['x'],c['y'],c['w'],c['h'],c['a'],round(c['cx'],1),round(c['cy'],1)) for c in comps])
json.dump(out,open('xcomps.json','w'))
