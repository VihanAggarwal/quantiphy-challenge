import cv2,numpy as np,sys
rend=sys.argv[1] if len(sys.argv)>1 else 'x'
for i in range(24,49):
    im=cv2.imread('frames/f%s_%02d.png'%(rend,i)).astype(int)
    b,g,r=im[...,0],im[...,1],im[...,2]
    notgreen=~((g>150)&(g>r+60)&(g>b+60))
    m=notgreen.astype(np.uint8)
    m[680:,1000:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    comps=[(st[k,4],st[k,0],st[k,1],st[k,2],st[k,3],cen[k]) for k in range(1,n) if st[k,4]>300]
    comps.sort(key=lambda c:-c[0])
    print(i, [(a,x,y,w,h,(round(c[0]),round(c[1]))) for a,x,y,w,h,c in comps[:5]])
