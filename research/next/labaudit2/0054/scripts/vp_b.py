from common import *
im=frames('b')[0]; g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
e=cv2.Canny(g,40,120)
mask=np.zeros_like(e); 
poly=np.array([[0,0],[760,0],[760,140],[600,200],[0,360]],np.int32)
cv2.fillPoly(mask,[poly],255); e=e&mask
L=cv2.HoughLinesP(e,1,np.pi/720,60,minLineLength=90,maxLineGap=8)
segs=[]
for l in L.reshape(-1,4):
    x1,y1,x2,y2=l; ang=np.degrees(np.arctan2(y2-y1,x2-x1))%180
    if 60<ang<120: segs.append(l)
segs=np.array(segs,float); print(len(segs))
for s in segs: print(s.astype(int), '%.1f'%(np.degrees(np.arctan2(s[3]-s[1],s[2]-s[0]))%180))
# VP: least squares intersection of lines (homogeneous)
Ls=[]
for x1,y1,x2,y2 in segs:
    l=np.cross([x1,y1,1],[x2,y2,1]); l=l/np.linalg.norm(l[:2]); Ls.append(l*np.hypot(x2-x1,y2-y1)**0.5)
Ls=np.array(Ls); _,_,Vt=np.linalg.svd(Ls); vp=Vt[-1]; vp=vp/vp[2]
print('VP',vp)
d=np.array([(vp[0]-CX)/F,(vp[1]-CY)/F,1.0]); d/=np.linalg.norm(d)
if d[1]<0: d=-d
print('down dir (cam coords)',d,'pitch(deg)=%.1f'%np.degrees(np.arcsin(d[2])),'roll=%.1f'%np.degrees(np.arctan2(d[0],d[1])))
out=im.copy()
for x1,y1,x2,y2 in segs.astype(int): cv2.line(out,(x1,y1),(x2,y2),(0,0,255),2)
cv2.imwrite(SCR+'/b_vp.png',out)
np.save(OUT+'/b_down.npy',d)
