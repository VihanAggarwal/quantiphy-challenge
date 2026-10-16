# orange-hue-only basketball mask in the original 'a' render (excludes the dark floor shadow that the ax SAM mask includes)
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from geom import *
R=0.116
for v in ['a','as']:
  for i in range(10,27):
    f=cv2.imread(f'{D}/{v}_{i:02d}.png')
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[:,:,0]<=20)&(hsv[:,:,1]>110)&(hsv[:,:,2]>70)).astype(np.uint8)
    m[:450,:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,l,st,c=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    mk=(l==k)
    nn,th,sd,_=cone_fit(mk)
    P,r=centre3d(nn,th,R)
    x,y,w,h=st[k,:4]
    print(v,i,'c=(%.1f,%.1f) %dx%d A=%d angdiam=%.3f r_c=%.3f r_s=%.3f sd=%.3f'%(c[k][0],c[k][1],w,h,st[k,4],2*np.degrees(th),r,r-R,sd),P.round(3))
