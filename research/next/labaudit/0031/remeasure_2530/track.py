import cv2, numpy as np, sys, json
D='/home/user/quantiphy-challenge/research/next/labaudit/0031/remeasure_2530/frames/'
render = sys.argv[1] if len(sys.argv)>1 else 'captured_0031x'
out=[]
for i in range(49):
    f=cv2.imread(D+'%s_%02d.png'%(render,i))
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    H,S,V=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    # white ball: low saturation, bright; restrict to table ROI
    roi=np.zeros(S.shape,bool); roi[380:520,560:720]=True
    wm=((S<60)&(V>150)&roi).astype(np.uint8)
    # yellow ball
    ym=((H>20)&(H<40)&(S>100)&(V>120)).astype(np.uint8); ym[:380]=0; ym[560:]=0
    res={'i':i}
    for name,m in [('white',wm),('tennis',ym)]:
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: res[name]=None; continue
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        cnts,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        (cx,cy),r=cv2.minEnclosingCircle(cnts[0])
        res[name]=dict(cx=float(cen[k][0]),cy=float(cen[k][1]),w=int(w),h=int(h),area=int(a),deq=float(2*np.sqrt(a/np.pi)),mec_d=2*r,mec_c=(cx,cy))
    out.append(res)
    w=res['white']; t=res['tennis']
    print(i, 'W' , None if w is None else (round(w['cx'],1),round(w['cy'],1),w['w'],w['h'],round(w['deq'],1)), 'T', None if t is None else (round(t['cx'],1),round(t['cy'],1),t['w'],t['h'],round(t['deq'],1)))
json.dump(out,open(D+'../track_%s.json'%render,'w'))
