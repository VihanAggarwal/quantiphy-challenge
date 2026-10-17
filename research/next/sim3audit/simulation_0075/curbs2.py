import cv2, numpy as np, sys, json
def roadmask(im):
    im=im.astype(int); B,G,R=im[...,0],im[...,1],im[...,2]
    return (abs(B-G)<6)&(abs(G-R)<6)&(B>135)&(B<200)
def scan_cols(mask, cols, vstart, vstop):
    """for each column scan upward from vstart; return first row where mask false (road edge)"""
    pts=[]
    for u in cols:
        col=mask[vstop:vstart+1,u][::-1]
        if not col[0]: continue
        k=np.argmin(col)  # first False
        if col[k]: continue
        pts.append((u, vstart-k+0.5))
    return np.array(pts,float)
def robust_line(P):
    u,v=P[:,0],P[:,1]; m=np.ones(len(u),bool)
    for it in range(6):
        a,b=np.polyfit(u[m],v[m],1); res=v-(a*u+b)
        s=1.4826*np.median(abs(res[m]))+0.3; m=abs(res)<3*s
    return a,b,np.sqrt(np.mean(res[m]**2)),int(m.sum()),len(u)
if __name__=='__main__':
    path=sys.argv[1]; spec=json.loads(sys.argv[2])
    im=cv2.imread(path); mask=roadmask(im)
    lines={}
    for name,(c0,c1,vs,ve) in spec.items():
        P=scan_cols(mask, range(c0,c1), vs, ve)
        a,b,rms,n,N=robust_line(P)
        lines[name]=(a,b); print(name,'v=%.5f u + %.2f rms %.2f n %d/%d'%(a,b,rms,n,N))
    if 'L' in lines and 'R' in lines:
        (a1,b1),(a2,b2)=lines['L'],lines['R']
        u=(b2-b1)/(a1-a2); v=a1*u+b1; print('VP u=%.1f v=%.1f'%(u,v))
