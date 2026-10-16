import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
pref=sys.argv[1] if len(sys.argv)>1 else '0020'
for i in range(49):
    im=cv2.imread(d+f'frames/{pref}_f{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    h,s,v=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    yel=((h>=20)&(h<=38)&(s>90)&(v>120)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(yel)
    out=[]
    for k in range(1,n):
        if st[k,4]>40: out.append((st[k,4],tuple(st[k,:4]),tuple(np.round(cen[k],1))))
    out.sort(reverse=True)
    print(i, out[:3])
