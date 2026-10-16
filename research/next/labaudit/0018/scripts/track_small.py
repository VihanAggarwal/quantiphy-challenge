from common import *
X=load('x')
# yellow-green tennis ball & yellow pineapple in x render: HSV
for i in range(24,49):
    hsv=cv2.cvtColor(X[i],cv2.COLOR_BGR2HSV)
    h,s,v=hsv[...,0].astype(int),hsv[...,1].astype(int),hsv[...,2].astype(int)
    m=((h>=20)&(h<=45)&(s>70)&(v>80)).astype(np.uint8)
    m[:, :600]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=sorted([(int(st[k][4]),int(st[k][0]),int(st[k][1]),int(st[k][2]),int(st[k][3])) for k in range(1,n) if st[k][4]>40],reverse=True)[:3]
    print(i,comps)
