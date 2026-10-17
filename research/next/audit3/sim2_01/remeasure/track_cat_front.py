import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0216_segmented.mp4')
rows=[]; i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    m=(g<60).astype(np.uint8)
    m[:,:]=m
    # restrict to y>820 (cat region) to avoid TV; cat body black
    m[:820,:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    # any non-white below the cat: paws (white paws!) -> use non-white mask in a box around cat
    nw=(f.astype(int).min(2)<235).astype(np.uint8)
    box=nw[max(0,y-80):1080, max(0,x-40):min(1920,x+w+60)]
    yy,xx=np.nonzero(box)
    rows.append((i,x,x+w-1,y,y+h-1,a,xs.mean(),ys.mean(), yy.max()+max(0,y-80)))
    i+=1
r=np.array(rows,float)
for row in r[::4]: print(' '.join(f'{v:.1f}' for v in row))
t=r[:,0]
for col,name in [(1,'left'),(2,'right'),(6,'cx')]:
    p=np.polyfit(t,r[:,col],1); res=r[:,col]-np.polyval(p,t)
    print(name,'slope %.3f'%p[0],'rms %.2f'%res.std())
print('bottom y (nonwhite) median %.1f max %.1f min %.1f'%(np.median(r[:,8]),r[:,8].max(),r[:,8].min()))
print('black-body bottom median', np.median(r[:,4]))
