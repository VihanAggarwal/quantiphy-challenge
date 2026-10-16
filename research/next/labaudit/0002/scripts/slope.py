import numpy as np
def P(p,d,f=711.):
    v=np.array([(p[0]-640)/f,(p[1]-360)/f,1.]); return d*v/np.linalg.norm(v)
# board top edge mid ~ (608.5,294), bottom edge mid ~ (613.5,419) (mask edges, frame 48)
for f in [700,711,730]:
    for ins in [0,3,6,10]:
        L=np.linalg.norm(P((608.5,294+ins),1.815,f)-P((613.5,419-ins),1.6715,f))
        print('f',f,'inset',ins,'px  L=%.1f cm'%(100*L))
# physical route on the table scale: bottom on table (range 1.589 @f711), top range from width ratio (board W from bottom width)
for f,rb in [(711,1.5886),(730,1.6307)]:
    W=103*rb/f; rt=W*f/97.7/0.9947
    L=np.linalg.norm(P((608.5,294),rt,f)-P((613.5,419),rb,f))
    print('table-scale physical: f',f,'board W %.1f cm'%(100*W),'top range %.3f'%rt,'L=%.1f cm'%(100*L))
# ToF-consistent with near end only (top range from width ratio, bottom stated 1.6715)
rb=1.6715; W=103*rb/711; rt=W*711/97.7/0.9947
print('near-end ToF + width ratio: W %.1f top range %.3f L=%.1f'%(100*W,rt,100*np.linalg.norm(P((608.5,294),rt)-P((613.5,419),rb))))
