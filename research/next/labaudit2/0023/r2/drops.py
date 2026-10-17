import cv2, numpy as np
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
F=[cv2.imread(R1+f'o{k:02d}.png').astype(np.float32).mean(2) for k in range(49)]
# regions: background people left/right (upper image), excluding board/book
regs={'left':(slice(150,330),slice(100,480)),'right':(slice(150,330),slice(720,1180)),'full':(slice(0,720),slice(0,1280))}
for name,(ys,xs) in regs.items():
    d=[np.abs(F[k+1][ys,xs]-F[k][ys,xs]).mean() for k in range(48)]
    print(name,' '.join('%d:%.2f'%(k,v) for k,v in enumerate(d)))
