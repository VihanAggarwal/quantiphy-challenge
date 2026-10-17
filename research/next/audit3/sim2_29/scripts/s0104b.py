from util import *
fr=frames('simulation_0104',idx={30})
g=fr[30].astype(np.float32)
bg=np.median(g[:, :300],axis=1)
for y in range(330,1080,6):
    d=np.abs(g[y]-g[y,100:300].mean(axis=0)).max(axis=1)
    w=np.where(d>18)[0]
    if len(w): print(y, w.min(), w.max(), w.max()-w.min()+1, g[y,960].astype(int))
