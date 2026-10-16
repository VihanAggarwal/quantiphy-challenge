import numpy as np
f=711.;CX=640;CY=360
def u(x,y):
    v=np.array([(x-CX)/f,(y-CY)/f,1.]);return v/np.linalg.norm(v)
tr=np.load('track_x.npy')
P0=1.321*u(482.5,185.8)
P46=1.5795*u(527.9,481.6)
# route A: down direction from labelled P0 and P46 (drop+rebound nearly the same vertical line)
d=(P46-P0)/np.linalg.norm(P46-P0)
print('down (labelled P0->P46):',d.round(4),' pitch deg',np.degrees(np.arcsin(d[2])))
def floor_below(P,d,R):
    b=P@d; c=P@P-R*R
    return -b+np.sqrt(b*b-c)
h=floor_below(P0,d,2.0285)
F=P0+h*d
print('route A: h0=%.4f m; floor pt pixel=(%.1f,%.1f)'%(h,CX+f*F[0]/F[2],CY+f*F[1]/F[2]))
H46=h-(P46-P0)@d
print('route A: apex height=%.4f'%H46)
# contact centre predicted
C=P0+(h-0.116)*d
print('pred contact centre pixel (%.1f,%.1f) range %.3f'%(CX+f*C[0]/C[2],CY+f*C[1]/C[2],np.linalg.norm(C)))
# Rebound trajectory: intersect each frame's ray with the vertical line through P46 (direction d), closest point
def on_line(x,y,A,d):
    v=u(x,y)
    # minimize |t v - (A + s d)| -> solve
    M=np.array([[v@v,-v@d],[-v@d,d@d]]); b=np.array([v@A,-(d@A)])
    t,s=np.linalg.solve(M,b)
    return s, np.linalg.norm(t*v-(A+s*d)), t
print('frame, s along down from P46 line, miss, range')
S=[]
for row in tr:
    i,x,y,r=row[:4]
    s,miss,t=on_line(x,y,P46,d)
    S.append((i,s,miss,t))
    print(int(i),round(s,4),round(miss,4),round(t,3))
S=np.array(S)
# fit rebound frames 38..48 parabola
for lo,hi in [(38,48),(39,48),(40,48),(38,46)]:
    m=(S[:,0]>=lo)&(S[:,0]<=hi)
    t=S[m,0]/24.; s=-S[m,1]  # height up
    p=np.polyfit(t,s,2)
    g=-2*p[0]; tap=-p[1]/(2*p[0])
    v18=abs(2*p[0]*1.8+p[1])
    print('rebound fit frames %d-%d: g_eff=%.2f apex t=%.3f v(1.8)=%.3f'%(lo,hi,g,tap,v18))
    # fixed g=9.8
    A=np.c_[np.ones_like(t),t]; y=s+4.9*t*t
    c,_,_,_=np.linalg.lstsq(A,y,rcond=None)
    tap2=c[1]/9.8; print('   g=9.8 fixed: apex t=%.3f v(1.8)=%.3f'%(tap2,abs(c[1]-9.8*1.8)))
