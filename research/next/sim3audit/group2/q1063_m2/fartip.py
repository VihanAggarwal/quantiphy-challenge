from load import frames; import numpy as np, cv2, json
F=frames(); bg=cv2.imread('bg.png').astype(int); sm=np.load('smooth.npy')
out={}
for i in range(60):
    cx,cy=sm[0,i],sm[1,i]; x0,y0=int(cx)-110,int(cy)-90
    c=F[i][y0:y0+180,x0:x0+220].astype(int); d=np.abs(c-bg[y0:y0+180,x0:x0+220]).sum(2)
    m=(d>35).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # keep components touching a 40px box around centre
    keep=np.zeros_like(m,bool)
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<6: continue
        if x< 110+60 and x+w>110-60 and y<90+50 and y+h>90-50: keep|=(lab==k)
    ys,xs=np.nonzero(keep); X=xs+x0; Y=ys+y0
    R=X>cx
    dist=np.hypot(X-cx,(Y-cy))
    j=np.argmax(np.where(R,dist,-1)); 
    L=X<cx; jl=np.argmax(np.where(L,dist,-1))
    out[i]=dict(far=(int(X[j]),int(Y[j])),near=(int(X[jl]),int(Y[jl])),top=int(Y.min()),bot=int(Y.max()),left=int(X.min()),right=int(X.max()))
    print(i,'c',(round(cx),round(cy)),'far',out[i]['far'],'nearfarthest',out[i]['near'],'top',out[i]['top'],'bot',out[i]['bot'])
json.dump(out,open('tips_auto.json','w'))
