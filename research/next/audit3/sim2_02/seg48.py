import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0248_segmented.mp4'); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
rows=[]
for i,im in enumerate(F):
    m=(im.astype(int).min(2)<235).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    L=sorted([(int(st[k,0]),int(st[k,1]),int(st[k,0]+st[k,2]-1),int(st[k,1]+st[k,3]-1),int(st[k,4]),round(cen[k,0],1),round(cen[k,1],1)) for k in range(1,n) if st[k,4]>60],key=lambda t:t[5])
    rows.append(L)
    if i%6==0 or i>=47: print(i,L)
json.dump(rows,open('seg48.json','w'))
