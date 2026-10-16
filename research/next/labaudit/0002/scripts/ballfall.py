import cv2, numpy as np
np.set_printoptions(linewidth=250)
# horizontal silhouette width of the falling ball against the green background (R-G signal)
for i,yr in [(41,range(494,512)),(42,range(495,530)),(43,range(525,575)),(44,range(565,620))]:
    f=cv2.imread(f'frames/f{i:02d}.png').astype(float)
    sig=f[...,2]-f[...,1]
    out=[]
    for y in yr:
        row=sig[y,560:680]
        bg=-46.0
        pk=np.percentile(row,95)
        if pk<0: continue
        lvl=(bg+pk)/2
        idx=np.nonzero(row>lvl)[0]
        # keep the largest contiguous run
        runs=np.split(idx,np.nonzero(np.diff(idx)>1)[0]+1)
        r=max(runs,key=len); a,b=r[0],r[-1]
        if a==0 or b==len(row)-1: continue
        xa=a-1+(lvl-row[a-1])/(row[a]-row[a-1]); xb=b+(row[b]-lvl)/(row[b]-row[b+1])
        out.append((y,xb-xa,560+(xa+xb)/2,pk))
    out=np.array(out)
    print(i,'rows',len(out),'top widths',np.round(np.sort(out[:,1])[-6:],1),'median',np.round(np.median(out[:,1]),1))
    print('   ',np.round(out[:,1],1))
