import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0192_segmented.mp4')
def sub(g,k):
    if 0<k<len(g)-1:
        a,b,cc=g[k-1],g[k],g[k+1]; den=(a-2*b+cc); return k+(0.5*(a-cc)/den if den!=0 else 0)
    return k
rows=[]; i=0
while True:
    ok,f=c.read()
    if not ok: break
    f=f.astype(float)
    s=f.sum(axis=2)
    # silhouette: non-white
    col=s[:, 830:930].mean(axis=1)
    nonw=np.nonzero(col<600)[0]
    nonw=nonw[nonw<560]
    top0=nonw.min()
    g=np.diff(col); 
    k=int(np.argmin(g[top0-5:top0+5]))+top0-5; ft=sub(-g,k)+0.5
    # silhouette bottom: last nonwhite before roof; search in rows top0..top0+320 the strongest positive gradient
    lo=top0+150; hi=min(top0+320,560)
    k=int(np.argmax(g[lo:hi]))+lo; sb=sub(g,k)+0.5
    # front-bottom: strongest negative drop in R (index 2) at cols 1040-1075 between top0+170 and sb-3
    r=f[:,1040:1075,2].mean(axis=1); gr=np.diff(r)
    lo2=int(top0+170); hi2=int(sb-4)
    fb=np.nan
    if hi2>lo2+2:
        k=int(np.argmin(gr[lo2:hi2]))+lo2; fb=sub(-gr,k)+0.5
    # widths at row ft+20 and at row sb-2
    def width(y):
        rr=s[int(y)]; nz=np.nonzero(rr[600:1300]<600)[0]
        return (nz.min()+600, nz.max()+600) if len(nz) else (np.nan,np.nan)
    wf=width(ft+30); wb=width(sb-1.5)
    rows.append((i,ft,fb,sb,wf[0],wf[1],wb[0],wb[1]))
    i+=1
o=np.array(rows,dtype=float)
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_20/s192_track.txt',o,fmt='%.2f')
for r in o[:80:5]: print(' '.join('%.1f'%x for x in r))
