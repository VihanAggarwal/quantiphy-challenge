import json, numpy as np, math
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0018/remeasure_b'
T=json.load(open(f'{OUT}/xtracks.json'))
cap=lambda v: math.floor(v*25/24+0.5)
def pts(name, frames):
    d=T[name]; fr=[i for i in frames if str(i) in d]
    return np.array([cap(i) for i in fr],float), np.array([d[str(i)]['c'][1] for i in fr])
for name,desc,asc,rad in [('soccer',range(31,40),range(40,49),22),('tennis',range(29,36),range(37,49),10)]:
    t1,y1=pts(name,desc); t2,y2=pts(name,asc)
    p1=np.polyfit(t1,y1,2); p2=np.polyfit(t2,y2,2)
    # intersection
    r=np.roots(p1-p2); r=[x.real for x in r if abs(x.imag)<1e-9 and t1.max()-1<x.real<t2.min()+1]
    for tc in r:
        yc=np.polyval(p1,tc)
        print(name,'contact cap=%.2f y_centre=%.1f floor_row~%.1f'%(tc,yc,yc+rad), 'v_in=%.1f v_out=%.1f px/f'%(np.polyval(np.polyder(p1),tc),np.polyval(np.polyder(p2),tc)))
    for H in (0.82,0.85,0.87,0.9):
        print('   H=%.2f -> Z_floor=%.2f'%(H, 711*H/(yc+rad-360)))
