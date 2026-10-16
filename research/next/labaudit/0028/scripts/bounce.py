import numpy as np
y={20:289.8,21:290.8,22:297.7,23:312.8,24:335.7,25:369.0,26:406.0,27:388.9,28:356.1,29:330.2,30:313.7,31:303.2,32:300.0,33:303.9,34:315.5,35:338.4,36:413.3,37:407.0,38:370.1,39:343.1,40:324.3,41:313.5,42:311.3,43:317.7,44:334.2,45:363.3,46:404.4,47:434.2,48:396.7}
def fit(a,b):
    t=np.arange(a,b+1); return np.polyfit(t,[y[i] for i in t],2)
down1=fit(22,25); up1=fit(27,35); up1b=fit(28,34)
up2=fit(38,45); up2b=fit(39,44)
def cross(p,q,lo,hi):
    r=np.roots(p-q); r=[x.real for x in r if abs(x.imag)<1e-9 and lo<x.real<hi]; return r
for name,u in [('up1',up1),('up1b',up1b)]:
    tb=cross(down1,u,24,28)
    apex=-u[1]/(2*u[0])
    print(name,'bounce1 t',np.round(tb,2),'y',[round(np.polyval(u,t),1) for t in tb],'apex',round(apex,2),'rise frames',[round(apex-t,2) for t in tb])
    for name2,v in [('up2',up2),('up2b',up2b)]:
        tb2=cross(u,v,34,39); 
        print('   ',name2,'bounce2 t',np.round(tb2,2),'y',[round(np.polyval(u,t),1) for t in tb2],'fall frames',[round(t-apex,2) for t in tb2])
# drop: start of free fall
print('down1 apex (release)',round(-down1[1]/(2*down1[0]),2))
for fps in (24,25):
    for T in (5.5,5.7,4.6):
        print(fps,'T frames',T,'h cm',round(0.5*980*(T/fps)**2,1))
