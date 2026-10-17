import cv2, numpy as np, sys
v=sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4'); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
rows=[]
for i,im in enumerate(F):
    m=(im.astype(int).min(2)<235).astype(np.uint8); m[:752]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    L=sorted([(int(st[k,0]),int(st[k,1]),int(st[k,0]+st[k,2]-1),int(st[k,1]+st[k,3]-1),int(st[k,4]),round(cen[k,0],1),round(cen[k,1],1)) for k in range(1,n) if st[k,4]>80],key=lambda t:t[6])
    rows.append(L)
print(len(F)); 
for i in (0,12,24,36,48,49): print(i,rows[i])
nobj=min(len(r) for r in rows[:49])
t=np.arange(49)
for k in range(nobj):
    a=np.array([r[k] for r in rows[:49]],float)
    w=a[:,2]-a[:,0]+1
    print('obj',k,'cy %.1f'%np.median(a[:,6]),'cx slope %.3f left %.3f right %.3f'%(np.polyfit(t,a[:,5],1)[0],np.polyfit(t,a[:,0],1)[0],np.polyfit(t,a[:,2],1)[0]),
          'width p10/50/90',np.percentile(w,[10,50,90]),'local cx 20-28 %.2f 16-32 %.2f'%((a[28,5]-a[20,5])/8,(a[32,5]-a[16,5])/16))
