import numpy as np
S=0.438/120.2
tr={'22A':np.load('simulation_0222_A.npy')[:,:2],'22B':np.load('simulation_0222_B.npy')[:,:2],'22C':np.load('simulation_0222_C.npy')[:,:2],'21C':np.load('simulation_0221_C.npy')[:,:2],'mean':np.load('Pmean.npy')}
def emu(P,f,hw,deg):
    i=np.arange(f-hw,f+hw+1)
    cx=np.polyfit(i-f,P[i,0],deg); cy=np.polyfit(i-f,P[i,1],deg)
    pm=lambda tt:np.array([np.polyval(cx,tt),np.polyval(cy,tt)])
    vb=lambda tt:np.linalg.norm(pm(tt)-pm(tt-1))*24*S
    # instantaneous
    dcx=np.polyder(cx); dcy=np.polyder(cy)
    vi=lambda tt: np.hypot(np.polyval(dcx,tt),np.polyval(dcy,tt))*24*S
    ai=(vi(0.01)-vi(-0.01))/0.02*24
    return vb(0),(vb(0)-vb(-1))*24,ai
for f in [12,24,48]:
    print('frame',f)
    for k,P in tr.items():
        row=[]
        for hw,deg in [(4,2),(5,3),(6,3),(7,4),(9,4)]:
            v,a,ai=emu(P,f,hw,deg); row.append(f'hw{hw}d{deg}: v={v:.3f} a_emu={a:.3f} a_inst={ai:.3f}')
        print(' ',k,' | '.join(row))
