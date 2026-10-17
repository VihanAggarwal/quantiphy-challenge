import cv2, numpy as np
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
bg=cv2.imread(S+'bg_a.png')
g=cv2.GaussianBlur(cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0)
gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
def fitline(xs, p0, p1, sign, band=10):
    pts=[]
    for x in xs:
        yg=p0[1]+(x-p0[0])*(p1[1]-p0[1])/(p1[0]-p0[0])
        lo=int(yg-band); hi=int(yg+band)
        col=sign*gy[lo:hi,x]
        i=np.argmax(col)
        if 0<i<len(col)-1 and col[i]>15:
            a,b,c=col[i-1],col[i],col[i+1]
            off=0.5*(a-c)/(a-2*b+c)
            pts.append((x,lo+i+off))
    pts=np.array(pts)
    A=np.c_[pts[:,0],np.ones(len(pts))]; y=pts[:,1]
    keep=np.ones(len(pts),bool)
    for it in range(5):
        sol,*_=np.linalg.lstsq(A[keep],y[keep],rcond=None)
        r=y-A@sol
        keep=np.abs(r)<max(0.8,2.5*np.std(r[keep]))
    print('n=%d/%d slope=%.5f icpt=%.2f rms=%.2f'%(keep.sum(),len(pts),sol[0],sol[1],np.std(r[keep])))
    return sol
# back wall top: bright above, dark below -> gy negative
L={}
print('back top'); L['bt']=fitline(list(range(470,580))+list(range(870,1090)),(455,180),(1100,120),-1)
print('left top'); L['lt']=fitline(range(45,440),(455,180),(37,70),-1)
# base: baseboard (dark) above floor (lighter): gy positive at baseboard bottom
print('back base'); L['bb']=fitline(list(range(475,610))+list(range(700,840))+list(range(880,1040)),(455,488),(1090,578),+1,band=12)
print('left base'); L['lb']=fitline(range(290,445),(455,488),(270,520),+1,band=12)
# baseboard top edge (wall gray -> dark baseboard): gy negative
print('back base top'); L['bbt']=fitline(list(range(475,610))+list(range(700,840))+list(range(880,1040)),(455,478),(1090,565),-1,band=10)
print('left base top'); L['lbt']=fitline(range(290,445),(455,478),(270,505),-1,band=10)
def inter(l1,l2):
    x=(l2[1]-l1[1])/(l1[0]-l2[0]); return np.array([x,l1[0]*x+l1[1]])
c=np.array([640,360.])
for a,b in [('bt','bb'),('bt','bbt')]:
    V1=inter(L[a],L[b]); print(a,b,'V1',V1)
for a,b in [('lt','lb'),('lt','lbt')]:
    V2=inter(L[a],L[b]); print(a,b,'V2',V2)
V1=inter(L['bt'],L['bb']); V2=inter(L['lt'],L['lb'])
d=-(V1-c)@(V2-c); print('f from orthogonal VPs (pp=centre):', np.sqrt(d) if d>0 else d)
V1b=inter(L['bt'],L['bbt']); V2b=inter(L['lt'],L['lbt'])
d=-(V1b-c)@(V2b-c); print('f (baseboard tops):', np.sqrt(d) if d>0 else d)
# corner point
print('corner from base lines', inter(L['bb'],L['lb']), 'top', inter(L['bt'],L['lt']))
np.save(S+'lines.npy',np.array([L[k] for k in ['bt','lt','bb','lb','bbt','lbt']]))
