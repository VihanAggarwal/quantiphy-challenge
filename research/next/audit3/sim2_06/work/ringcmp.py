import numpy as np,subprocess,re,sys
def run(v,roi):
    out=subprocess.run(['.venv/bin/python','research/next/audit3/sim2_06/work/bgtrack.py',v,roi,'40'],capture_output=True,text=True).stdout
    rows=[]
    for l in out.splitlines():
        if l.startswith('('):
            nums=[float(x) for x in re.findall(r'\(([-\d.]+)\)',l)]
            i=int(l[1:l.index(',')])
            rows.append([i]+nums)
    return np.array(rows)
T=run('simulation_0228','(300,630,1500,1000)')
F=run('simulation_0227_segmented','(560,850,1300,1080)')
G=run('simulation_0227','(560,950,1300,1080)')
for name,A in [('top',T),('front_seg',F),('front_raw_lowerpart',G)]:
    t=A[:,0]; L=A[:,1]; R=A[:,2]; c=A[:,5]
    mid=(L+R)/2
    good=np.ones(len(t),bool)
    if name=='front_seg': good&=~np.isin(t,[6,7,8])
    print(name,'total disp L %.1f R %.1f'%(L[-1]-L[0],R[-1]-R[0]))
    # local quadratic fit around frame 12 of left/right/centroid -> backward-diff equivalent velocity at 11.5
    for key,s in [('L',L),('R',R),('mid',mid),('cx',c)]:
        w=good&(t>=6)&(t<=18)
        p=np.polyfit(t[w],s[w],2)
        v=np.polyval(p,12)-np.polyval(p,11)
        print('  %s v(11.5)=%.2f px/f  raw diff12=%.1f'%(key,v,s[t==12][0]-s[t==11][0]))
    d=np.diff(mid); print('  mid diffs',np.round(d,1).tolist())
