import numpy as np,json
exec(open('plane.py').read().split('for f in')[0])
T=json.load(open('track_raw.json'))
cap=lambda i:int(np.floor(i*25/24+0.5))
for f,h in [(711,17.0),(711,17.83),(699.2,17.0)]:
    n,X,L,ang,Ki=plane(f)
    print(f'--- f={f} h={h}')
    rows=[]
    for i in range(18,49):
        x,y=T['x'][i][1],T['x'][i][2]
        r=Ki@np.array([x,y,1.]); Cc=r*(h-3.35)/(n@r)
        rows.append((i,cap(i),np.linalg.norm(Cc),Cc))
    for k,(i,c,R,Cc) in enumerate(rows):
        s=''
        if k+1<len(rows):
            i2,c2,R2,C2=rows[k+1]; s=f'step={np.linalg.norm(C2-Cc):6.2f}cm dcap={c2-c} v={np.linalg.norm(C2-Cc)*25/(c2-c):6.1f}cm/s'
        print(f'v{i:02d} c{c:02d} t={c/25:.2f} range_ctr={R:6.1f} surf={R-3.35:6.1f} C={Cc.round(1)} {s}')
