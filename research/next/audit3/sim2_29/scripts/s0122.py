from util import *
fr=frames('simulation_0122',gray=True)
bgA=np.median(np.stack([fr[i] for i in range(22,40)]),axis=0).astype(np.float32)
bgB=np.median(np.stack([fr[i] for i in range(0,6)]),axis=0).astype(np.float32)
bg=bgA.copy(); bg[740:]=bgB[740:]
# find sword column
d=np.abs(fr[13].astype(np.float32)-bg)
print('col of max', np.argmax(d[600:1000].sum(axis=0)))
for i in range(0,18):
    d=np.abs(fr[i].astype(np.float32)-bg)[:,556:596]
    prof=np.sort(d,axis=1)[:,-6:].mean(axis=1)  # top-6 mean per row
    on=prof>35
    # longest run
    best=(0,0,0); s=None
    for y in range(len(on)+1):
        if y<len(on) and on[y]:
            if s is None: s=y
        else:
            if s is not None:
                if y-s>best[0]: best=(y-s,s,y-1)
                s=None
    print(i,best)
