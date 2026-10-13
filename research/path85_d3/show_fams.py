from common import *
nl = pd.read_pickle(OUT / "audit_nl.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_colwidth", 60)
g = nl.groupby(["fam_size", "video_id"]).agg(cat=("category", lambda s: "".join(sorted(set(s)))), n=("cur", "size"),
    fact=("status", lambda s: (s == "fact").sum()), mod=("status", lambda s: (s == "modified").sum()),
    raw=("status", lambda s: (s == "ens_raw").sum()), prior=("prior", "first"))
print(g.to_string())
