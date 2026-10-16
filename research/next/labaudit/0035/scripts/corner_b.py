import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from recon import F,CX,CY,ray
L=[(280,368),(290,362),(300,357),(310,352),(320,345),(330,340),(340,334),(350,330),(360,326),(370,320),(380,314),(390,310),(400,303),(410,298),(420,293),(430,287),(440,282),(450,279),(460,272),(470,266),(480,260),(490,255),(500,248),(510,242),(520,240),(530,234),(540,226),(550,224),(560,218),(570,212),(580,207)]
R=[(640,199),(650,201),(660,203),(670,204),(680,207),(690,210),(700,212),(710,213),(720,216),(730,217),(740,220),(750,221),(760,225),(770,225),(780,226),(790,230),(800,232),(810,233),(820,235)]+[(x,y) for x,y in [(960,263),(970,263),(980,266),(990,268),(1000,270),(1010,272),(1020,274),(1030,275),(1040,277),(1050,281),(1060,282),(1070,283),(1080,285),(1090,288),(1100,291),(1110,293),(1120,295),(1130,297),(1140,297),(1150,300),(1160,303),(1170,305),(1180,306),(1190,309),(1200,311),(1210,312),(1220,315),(1230,317),(1240,319),(1250,321),(1260,323)]]
V=[(577,30),(579,40),(581,50),(584,60),(585,70),(585,80),(590,90),(585,100),(592,110),(587,120),(589,130),(591,140),(599,150),(601,160)]
def plane_normal_of_line(pts):
    # back-projection plane normal: fit 3D rays to a plane through origin
    Rr=np.array([ray(u,v) for u,v in pts]); u,s,vt=np.linalg.svd(Rr); return vt[2], s
mL,sL=plane_normal_of_line(L); mR,sR=plane_normal_of_line(R); mV,sV=plane_normal_of_line(V)
print('line fit sing (straightness):',sL[2],sR[2],sV[2])
# Solve: d1 in plane perp mL, d2 = n x d1 perp mR, n perp d1, n perp mV
def basis(m):
    a=np.cross(m,[1,0,0]); a/=np.linalg.norm(a); b=np.cross(m,a); return a,b
a1,b1=basis(mL)
best=[]
for th in np.linspace(0,np.pi,36001):
    d1=np.cos(th)*a1+np.sin(th)*b1
    n=np.cross(d1,mV); n/=np.linalg.norm(n)
    d2=np.cross(n,d1)
    best.append((abs(d2@mR),th,n,d1,d2))
best.sort(key=lambda x:x[0])
for e,th,n,d1,d2 in best[:3]:
    if n[1]>0: n=-n
    print('resid',e,'n',np.round(n,4),'pitch deg %.1f'%np.degrees(np.arcsin(-n[2])),'roll deg %.1f'%np.degrees(np.arctan2(n[0],-n[1])))
# Alternative without V: family over theta with d1 perp d2 constraint -> report n for each
fam=[]
a2,b2=basis(mR)
for th in np.linspace(0,np.pi,3601):
    d1=np.cos(th)*a1+np.sin(th)*b1
    # d2 in plane perp mR and perp d1: d2 = mR x d1
    d2=np.cross(mR,d1); 
    if np.linalg.norm(d2)<1e-6: continue
    d2/=np.linalg.norm(d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    if n[1]>0: n=-n
    fam.append((th,n))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/fam_b.npy',np.array([np.r_[t,n] for t,n in fam]))
