import cv2,numpy as np,sys
v=sys.argv[1]
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
F=[]
for i in range(62):
    ok,im=c.read(); F.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
fps=120.
# template: front-face texture patch from frame 58 (box nearly at bottom), rows 230..330 (front face), cols 560..900
ref=58
y0,y1,x0,x1=250,340,560,900
T=F[ref][y0:y1,x0:x1]
res=[]
for i in range(0,59):
    img=F[i]
    r=cv2.matchTemplate(img[:, x0-5:x1+5],T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    yy=loc[1]; xx=loc[0]
    # subpixel parabola in y
    if 0<yy<r.shape[0]-1:
        a,b,cc=r[yy-1,xx],r[yy,xx],r[yy+1,xx]; dy=0.5*(a-cc)/(a-2*b+cc)
    else: dy=0
    res.append((i,yy+dy-y0,mx))
res=np.array(res)
ok=res[:,0]>=0
# template must be fully inside: patch top y0 + shift >=0
good=(res[:,1]+y0>=0)&(res[:,2]>0.8)
t=res[good,0]/fps; y=res[good,1]
p=np.polyfit(t,y,2); print('texture (front face) n=%d a=%.1f px/s2 vertex t=%.4f rms=%.3f'%(good.sum(),2*p[0],-p[1]/(2*p[0]),(y-np.polyval(p,t)).std()))
for lo in (10,20,30):
    g2=good&(res[:,0]>=lo); t2=res[g2,0]/fps; p2=np.polyfit(t2,res[g2,1],2); print('  from frame',lo,'a=%.1f'%(2*p2[0]),'vertex %.4f'%(-p2[1]/(2*p2[0])))
print('corr min',res[good,2].min())
# edges from mask (non-white in segmented / brown in original)
top=[];bot=[]
for i in range(59):
    im=F[i]
    if 'segmented' in v:
        m=(im<200)
    cols=m[:,580:800].mean(1)
    ys=np.nonzero(cols>0.5)[0]
    # subpixel: use fractional coverage sum around edges
    top.append(ys.min()); bot.append(ys.max())
top=np.array(top,float);bot=np.array(bot,float)
idx=np.arange(59)
for nm,arr,a0 in [('far-bottom edge',bot,0),('far-bottom edge f>=10',bot,10),('top edge (front) f>=30',top,30)]:
    g=idx>=a0
    if 'top' in nm: g&=arr>0
    t=idx[g]/fps; p=np.polyfit(t,arr[g],2)
    print(nm,'a=%.1f vertex %.4f rms %.3f'%(2*p[0],-p[1]/(2*p[0]),(arr[g]-np.polyval(p,t)).std()))
