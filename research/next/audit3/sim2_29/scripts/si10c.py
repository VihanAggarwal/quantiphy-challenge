from util import *
fr=frames('internet_0010_segmented')
D=[]
for i in range(48,80):
    f=fr[i].astype(np.float32)
    g=f.min(axis=2)
    m=(g<200).astype(np.uint8); m[440:]=0; m[:,:440]=0
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    sub=g[y-4:y+h+4,x-4:x+w+4]
    inner=np.percentile(sub,10)  # dark interior level
    cov=np.clip((255-sub)/(255-inner),0,1)
    A=cov.sum(); D.append((i,2*np.sqrt(A/np.pi),w,h,inner))
D=np.array(D)
print(np.round(D,1))
print('median coverage eq diam',np.median(D[:,1]),'mean',D[:,1].mean())
