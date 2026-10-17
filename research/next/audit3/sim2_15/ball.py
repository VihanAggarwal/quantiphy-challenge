from util import *
import sys
v=sys.argv[1]
fr=frames(v)
C=[];R=[]
for i,f in enumerate(fr):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    h=hsv[:,:,0].astype(int)
    m=(((h>=155)|(h<=1))&(hsv[:,:,1]>70)&(hsv[:,:,2]>25)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    nn,lab,stats,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(stats[1:,4]); s=stats[k]
    C.append((cen[k][0],cen[k][1],s[1])); R.append((s[2],s[3],s[1],s[1]+s[3],s[4]))
C=np.array(C); R=np.array(R)
print('w,h median',np.median(R[:,0]),np.median(R[:,1]), 'equiv diam from area',np.median(2*np.sqrt(R[:,4]/np.pi)))
for i in range(len(fr)): print(i,'%.2f %.2f'%tuple(C[i][:2]),R[i])
np.savetxt(W+f'ball_{v}.txt',np.c_[C,R])
