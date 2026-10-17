import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0010.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.int16))
fr=np.array(fr); print(fr.shape)
med=np.median(fr,axis=0)
for i in range(len(fr)):
    d=np.abs(fr[i]-med)>40
    d=d.astype(np.uint8)
    d=cv2.morphologyEx(d,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(d)
    big=[(st[k,4],k) for k in range(1,n)]
    big.sort(reverse=True)
    s=' '.join('[%d: x%d-%d y%d-%d a%d c(%.0f,%.0f)]'%(k,st[k,0],st[k,0]+st[k,2],st[k,1],st[k,1]+st[k,3],st[k,4],cen[k,0],cen[k,1]) for a,k in big[:3])
    print(i,s)
