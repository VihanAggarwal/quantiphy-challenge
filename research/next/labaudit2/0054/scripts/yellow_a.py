from common import *
L=frames('a')
for k in range(20,40):
    im=L[k]; h=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=cv2.inRange(h,np.array((22,90,110)),np.array((45,255,255)))
    m[:200]=0; m[:, :250]=0; m[:,720:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    for i in range(1,n):
        if st[i,4]<25: continue
        ys,xs=np.nonzero(lab==i)
        print(k,cap(k),'(%.1f,%.1f) bb=(%.1f,%.1f) %dx%d A=%d'%(cen[i][0],cen[i][1],(xs.min()+xs.max())/2,(ys.min()+ys.max())/2,st[i,2],st[i,3],st[i,4]))
