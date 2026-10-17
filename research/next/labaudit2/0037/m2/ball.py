import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0037x.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
med=cv2.imread('median_x.png').astype(int)
for i,f in enumerate(fr):
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(int)
    d=np.abs(f.astype(int)-med).sum(2)
    m=((d>60)&(g>90)).astype(np.uint8)
    m[400:,:]=0  # restrict to above table region roughly
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    # equivalent diameter
    print(i, 'c=(%.1f,%.1f) w=%d h=%d area=%d eqd=%.1f'%(cen[k][0],cen[k][1],w,h,a,2*np.sqrt(a/np.pi)))
