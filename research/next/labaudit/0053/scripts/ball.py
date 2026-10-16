import cv2, numpy as np
for prefix in ['o','s']:
    fr=[cv2.imread(f'frames/{prefix}_{n:02d}.png').astype(float) for n in range(16,48,2)]  # bin far from ball after n~5
    med=np.median(np.stack(fr),0)
    # use red-ish channel contrast: ball orange
    b,g,r=med[...,0],med[...,1],med[...,2]
    sat=r-b  # orange high
    sat=cv2.GaussianBlur(sat,(0,0),0.7)
    gx=np.zeros_like(sat); gx[:,1:-1]=(sat[:,2:]-sat[:,:-2])/2
    gy=np.zeros_like(sat); gy[1:-1,:]=(sat[2:,:]-sat[:-2,:])/2
    def sub(p,i):
        if i==0 or i==len(p)-1: return i
        a,b_,c=p[i-1],p[i],p[i+1]; d=a-2*b_+c; return i+(0.5*(a-c)/d if d!=0 else 0)
    W=[]
    for y in range(355,386):
        pl=gx[y,940:975]; pr=-gx[y,1000:1035]
        xl=940+sub(pl,np.argmax(pl)); xr=1000+sub(pr,np.argmax(pr)); W.append((y,xl,xr,xr-xl))
    W=np.array(W); i=np.argmax(W[:,3])
    Hs=[]
    for x in range(970,1002):
        pt=gy[325:355,x]; pb=-gy[385:415,x]
        yt=325+sub(pt,np.argmax(pt)); yb=385+sub(pb,np.argmax(pb)); Hs.append((x,yt,yb,yb-yt))
    Hs=np.array(Hs); j=np.argmax(Hs[:,3])
    print(prefix,'max width %.1f at y %d (L %.1f R %.1f); median top5 %.1f'%(W[i,3],W[i,0],W[i,1],W[i,2],np.sort(W[:,3])[-5:].mean()))
    print(prefix,'max height %.1f at x %d (T %.1f B %.1f); median top5 %.1f'%(Hs[j,3],Hs[j,0],Hs[j,1],Hs[j,2],np.sort(Hs[:,3])[-5:].mean()))
