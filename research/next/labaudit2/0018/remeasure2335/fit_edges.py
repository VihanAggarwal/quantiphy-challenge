import numpy as np
f=711.; fps=25.; g=9.8
t=np.array([28,29,30,31,32,33,34,35,37,38,39],float)
bot=np.array([291,295,305,322,337,361,387,418,491,531,576],float)
top=np.array([236,238,245,260,270,290,316,345,410,450,494],float)
def acc(tt,yy):
    c=np.polyfit(tt,yy,2); r=yy-np.polyval(c,tt); return 2*c[0], np.sqrt(np.mean(r**2))
for lab,y in [('bottom',bot),('top',top),('mid',(bot+top)/2)]:
    for lo in [29,30,31,32,33]:
        sel=t>=lo
        a,r=acc(t[sel],y[sel]); print('%s from c%d: a=%.2f px/fr2 rms %.1f -> Z(no drag)=%.2f m'%(lab,lo,a,r,f*g/(a*fps**2)))
