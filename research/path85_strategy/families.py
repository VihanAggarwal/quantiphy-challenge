"""Scene-family id per video (size-link families of qp.postprocess), cached for clustering."""
from common import *
import qp.postprocess as pp
t = pd.read_pickle(OUT / "table.pkl").reset_index()
df = pp._questions(t)
facts = pp._parse_facts(df)
links = pp.scene_links(df, facts, pp.FrameCache(pp.DEFAULT_CACHE))
fam = pp.scene_families(df, links, pp.SIZE_LINKS)
famm = pp.scene_families(df, links, pp.MOTION_LINKS)
out = pd.DataFrame({"video_id": list(fam), "fam": [fam[v] for v in fam], "famm": [famm.get(v) for v in fam]})
out.to_csv(OUT / "families.csv", index=False)
print(out.fam.nunique(), out.famm.nunique(), len(out))
