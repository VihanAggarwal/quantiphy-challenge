"""Speed profile along the track (plane and size routes), sliding quadratic fits (+-4 capture frames)."""
import numpy as np, json
B='/home/user/quantiphy-challenge/research/next/labaudit2/0031/'
R=json.load(open(B+'routes_f711.json'))
for ball in ('T','W'):
    rows=R[ball]; n=np.array([r['n'] for r in rows]); k=np.array([r['k'] for r in rows])
    print('ball',ball)
    for key in ('Pp','Ps'):
        P=np.array([r[key] for r in rows]); line=[]
        for c in range(18, n.max()-1, 2):
            s=np.abs(n-c)<=4
            if s.sum()<6: continue
            v=np.array([np.polyval(np.polyder(np.polyfit(n[s]/25,P[s,j],2)),c/25) for j in range(3)])
            line.append('n%d:%.0f'%(c,np.linalg.norm(v)))
        print(' ',key,' '.join(line))
    # distance travelled (plane route) from rest position
    P=np.array([r['Pp'] for r in rows]); P0=P[(n<=15)].mean(0)
    print('  plane-route distance from rest:', ' '.join('k%d:%.1f'%(kk,np.linalg.norm(p-P0)) for kk,p in zip(k,P) if kk%2==0))
