import cv2, numpy as np
f=cv2.imread('frames/f48.png')
hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
wood=((H>=5)&(H<=30)&(S>40)&(V>60))
wood=cv2.morphologyEx(wood.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8)).astype(bool)
def hom_line(pts):
    pts=np.array(pts,float); m=pts.mean(0); u,s,vt=np.linalg.svd(pts-m); d=vt[0]; n=np.array([-d[1],d[0]])
    return np.array([n[0],n[1],-n@m]), np.std((pts-m)@n)
R=[(600+np.nonzero(wood[y,600:900])[0].max()+0.5,y) for y in range(330,470)]
L=[(400+np.nonzero(wood[y,400:600])[0].min()-0.5,y) for y in range(400,478)]
Bk=[(x,250+np.nonzero(wood[250:400,x])[0].min()-0.5) for x in range(668,722)]
# front top edge: first row where V drops below 140 scanning down from 450
F=[]
for x in range(490,770,5):
    col=V[450:520,x]; k=np.nonzero(col<140)[0][0]; 
    # subpixel: linear interp between k-1 and k at 140 level
    y=450+k-1+(col[k-1]-140)/(col[k-1]-col[k]); F.append((x,y))
lines={}
for nm,p in [('right',R),('left',L),('back',Bk),('front',F)]:
    l,s=hom_line(p); lines[nm]=l; print(nm,'resid std',round(s,2),'n',len(p))
def X(a,b):
    p=np.cross(lines[a],lines[b]); return p[:2]/p[2]
FL=X('front','left'); FR=X('front','right'); BR=X('back','right')
print('FL',FL,'FR',FR,'BR',BR)
v1=X('left','right'); v2=X('front','back')
print('vp depth',v1,'vp width',v2)
c=np.array([640,360.])
f2=-(v1-c)@(v2-c); print('f from orthogonal VPs',np.sqrt(f2) if f2>0 else f2)
np.save('scripts/table_pts.npy',np.array([FL,FR,BR]))
np.save('scripts/table_lines.npy',np.array([lines[k] for k in ['front','right','back','left']]))
