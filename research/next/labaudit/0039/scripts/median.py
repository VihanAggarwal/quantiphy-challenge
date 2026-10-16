import cv2, numpy as np
B='/home/user/quantiphy-challenge/research/next/labaudit/0039'
for r in ['0039','0039s','0039x']:
    fr=np.stack([cv2.imread(f'{B}/frames/{r}_{i:02d}.png') for i in range(49)])
    med=np.median(fr,axis=0).astype(np.uint8)
    cv2.imwrite(f'{B}/median_{r}.png',med)
    np.save(f'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/fr_{r}.npy',fr)
