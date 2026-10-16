import cv2, numpy as np, json
T=json.load(open('scripts/trk_o.json'))
for k in [8,21,22,34]:
    im=cv2.imread(f'frames/captured_0036/f{k:02d}.png').astype(float).mean(2)
    u,v=T[str(k)]['cx'],T[str(k)]['cy']; ui,vi=int(round(u)),int(round(v))
    print(k,u,v)
    print(' vert', ' '.join('%d:%d'%(y,im[y,ui-2:ui+3].mean()) for y in range(vi-25,vi+25)))
    print(' horz', ' '.join('%d:%d'%(x,im[vi-2:vi+3,x].mean()) for x in range(ui-40,ui+40,2)))
