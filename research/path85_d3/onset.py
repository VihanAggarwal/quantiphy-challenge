"""Motion onset in clips whose prior states a constant acceleration 'before T' / from rest: first frame whose
difference to frame 0 exceeds noise. Test inputs (frames) only."""
from common import *
import cv2, sys
t = test_df().set_index('qid')
vids = sys.argv[1:] or ['simulation_0202', 'simulation_0205', 'simulation_0206', 'simulation_0209', 'simulation_0188',
                        'simulation_0188_segmented', 'simulation_0201', 'simulation_0180', 'simulation_0300', 'simulation_0301',
                        'simulation_0159', 'simulation_0182', 'simulation_0184', 'simulation_0186', 'simulation_0198', 'simulation_0199', 'simulation_0200']
for v in vids:
    r = t[t.video_id == v].iloc[0]
    cap = cv2.VideoCapture(r.video_path)
    fr = []
    while len(fr) < 30:
        ok, f = cap.read()
        if not ok: break
        fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.int16))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps_c = cap.get(cv2.CAP_PROP_FPS)
    d0 = [int((np.abs(fr[i] - fr[0]) > 25).sum()) for i in range(1, len(fr))]
    dd = [int((np.abs(fr[i] - fr[i - 1]) > 25).sum()) for i in range(1, len(fr))]
    print(v, 'fps', r.fps, 'container', round(fps_c, 2), 'frames', n, '| prior:', r.prior.replace('\n', '; ')[:60])
    print('   changed px vs frame0:', d0[:14])
    print('   changed px vs prev  :', dd[:14])
