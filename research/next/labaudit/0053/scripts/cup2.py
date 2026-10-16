import cv2, numpy as np
def widths(prefix,label):
    fr=[cv2.imread(f'frames/{prefix}_{n:02d}.png').astype(float) for n in range(0,48)]
    med=np.median(np.stack(fr),0)
    out=[]
    for ch in ['gray']:
        g=med.mean(2)
        g=cv2.GaussianBlur(g,(0,0),0.7)
        gx=np.zeros_like(g); gx[:,1:-1]=(g[:,2:]-g[:,:-2])/2
        for y in range(402,450,2):
            pl=np.abs(gx[y,540:562]); pr=np.abs(gx[y,566:590])
            il=np.argmax(pl); ir=np.argmax(pr)
            def sub(p,i):
                if i==0 or i==len(p)-1: return i
                a,b,c=p[i-1],p[i],p[i+1]; d=a-2*b+c; return i+(0.5*(a-c)/d if d!=0 else 0)
            xl=540+sub(pl,il); xr=566+sub(pr,ir)
            out.append((y,xl,xr,xr-xl,pl[il],pr[ir]))
    print(label)
    for o in out: print('  %d L %.1f R %.1f W %.1f  (%.0f,%.0f)'%o)
widths('s','s-render')
