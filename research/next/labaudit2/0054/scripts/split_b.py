from common import *
from bgsub import bg
B=bg('b')
boxes={20:(170,380,290,480),21:(200,330,310,420),22:(180,290,330,370),23:(230,250,380,330),24:(285,220,420,300),25:(330,195,450,280),26:(375,180,485,265),27:(420,170,520,260),28:(450,170,550,265)}
for k,(x0,y0,x1,y1) in boxes.items():
    im=frames('b')[k]; d=np.abs(im.astype(np.int16)-B).sum(2)
    m=(d>45)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    sub=np.zeros(m.shape,bool); sub[y0:y1,x0:x1]=True; m&=sub
    yel=m&(hsv[...,1]>95)&(hsv[...,0]>18)&(hsv[...,0]<40)
    wht=m&(hsv[...,1]<45)&(hsv[...,2]>150)
    out=[]
    for nm,mm in [('G',yel),('W',wht)]:
        mm=cv2.morphologyEx(mm.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(mm)
        if n<2: out.append(f'{nm}: none'); continue
        i=1+np.argmax(st[1:,4]); ys,xs=np.nonzero(lab==i)
        out.append(f'{nm}: ({cen[i][0]:.1f},{cen[i][1]:.1f}) {st[i,2]}x{st[i,3]} A={st[i,4]}')
    print(k,cap(k),' | '.join(out))
    crop=im[y0:y1,x0:x1].copy(); 
    vis=np.hstack([crop,np.dstack([yel[y0:y1,x0:x1]*255,wht[y0:y1,x0:x1]*255,np.zeros_like(crop[...,0])]).astype(np.uint8)])
    cv2.imwrite(SCR+f'/bsplit_{k}.png',cv2.resize(vis,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
