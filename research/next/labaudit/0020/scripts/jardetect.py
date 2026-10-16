import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
pref=sys.argv[1] if len(sys.argv)>1 else '0020'
vthr=int(sys.argv[2]) if len(sys.argv)>2 else 200
for i in range(49):
    im=cv2.imread(d+f'frames/{pref}_f{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
    s,v=hsv[...,1],hsv[...,2]
    m=((s<45)&(v>vthr)).astype(np.uint8)
    m[:, 850:]=0   # vent box
    m[680:,:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=[(int(st[k,4]),tuple(int(x) for x in st[k,:4]),tuple(np.round(cen[k],1))) for k in range(1,n) if st[k,4]>40]
    out.sort(reverse=True)
    print(i,out[:4])
