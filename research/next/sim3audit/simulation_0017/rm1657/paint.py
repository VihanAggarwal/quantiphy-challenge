import cv2,numpy as np
bg=cv2.imread('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/frames/orig_bg.png'); g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(float)
def cross(col,thr,v0,first=True):
    idx=np.nonzero(col>thr)[0]
    if not len(idx): return np.nan
    if first:
        k=idx[0]; a,b=col[k-1],col[k]; return v0+k-1+(thr-a)/(b-a)
    k=idx[-1]
    if k+1>=len(col): return np.nan
    a,b=col[k],col[k+1]; return v0+k+(a-thr)/(a-b)
res={}
import sys
RR=range(int(sys.argv[1]),int(sys.argv[2]),2); LL=range(int(sys.argv[3]),int(sys.argv[4]),2)
for name,us in (('R',RR),('L',LL)):
    out=[]
    for u in us:
        col=g[465:598,u]
        t=cross(col,170,465,True); b=cross(col,170,465,False)
        out.append((u,t,b,b-t))
    arr=np.array(out); m=np.isfinite(arr).all(1); arr=arr[m]
    ph=np.polyfit(arr[:,0],arr[:,3],1); pt=np.polyfit(arr[:,0],arr[:,1],1); pb=np.polyfit(arr[:,0],arr[:,2],1)
    print(name,'n=%d height fit h(u)= %.4f*u + %.2f ; h at ends %.2f %.2f ; top slope %.4f bot slope %.4f'%(len(arr),ph[0],ph[1],np.polyval(ph,arr[0,0]),np.polyval(ph,arr[-1,0]),pt[0],pb[0]))
    print('   relative dZ/Z per 100px: %.4f'%(-ph[0]*100/np.polyval(ph,arr[:,0].mean())))
    # painting horizontal extents at mid rows
    for v in (500,530,560):
        row=g[v, (670 if name=='R' else 300):(780 if name=='R' else 405)]
        u0=(670 if name=='R' else 300)
        l=cross(row,170,u0,True); r=cross(row,170,u0,False)
        print('   row %d painting u %.1f..%.1f'%(v,l,r))
