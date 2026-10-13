"""Lab prop sizes from the QuantiPhy paper's Table 6 (measured prop dimensions; public, App. Table 6 of
arXiv 2512.19526; research/webintel/table6_props.csv). Validation (evaluation only): the 10 validation lab size
questions that name a Table-6 prop all have label == Table 6 (research/webintel/table6_check_out.txt).
Rules map a lab size question (video family + wording) to a Table-6 value. Tiers:
  A  unambiguous prop and dimension (named ball / cup / pen / cookie / slope board / bottle / pencil case / tape)
  B  prop identity checked on frames here (0062 large whiteboard on the floor, 0037 glass jar whose ToF depth reads
     through the glass, 0053 white-covered book, 0062 / 0018 white food box length)
Not used: notebook (validation 0013 notebook width label 10.8 != Table-6 green notebook 8.8), trashbin (printed
dims ambiguous), stuffed toys / white jar / poker tower (identity or dimension unclear)."""
import re
RULES = [  # (tier, family regex or None, question regex, value_cm, name)
    ("A", None, r"yoga ball.*diameter|diameter of the yoga ball|yoga ball's diameter", 52.2, "yoga ball d"),
    ("A", None, r"diameter of the soccer ball|soccer ball's diameter", 17.5, "soccer ball d"),
    ("A", None, r"basketball's diameter|diameter of the basketball", 23.2, "basketball d"),
    ("A", None, r"diameter of the tennis ball", 6.7, "tennis ball d"),
    ("A", None, r"height of the pink bottle", 19.5, "pink bottle h"),
    ("A", None, r"height of the pencil bag", 6.7, "pencil case h"),
    ("A", None, r"length of the pencil bag", 21.0, "pencil case l"),
    ("A", None, r"height of the (white )?cup", 14.5, "white cup h"),
    ("A", None, r"rim of the white cup", 8.6, "white cup d"),
    ("A", None, r"diameter of the cookie", 8.0, "toy cookie d"),
    ("A", None, r"length of the pen\b", 14.5, "black pen l"),
    ("A", None, r"length of the slope", 30.8, "small whiteboard l"),
    ("A", None, r"width of the slope", 23.2, "small whiteboard w"),
    ("A", None, r"diameter of the tape|width of the tape", 10.1, "tape d"),
    ("B", r"captured_0062", r"length of the whiteboard", 81.0, "large whiteboard l"),
    ("B", r"captured_0062", r"width of the whiteboard", 60.0, "large whiteboard w"),
    ("B", r"captured_0037", r"height of the glass jar", 8.5, "glass jar h"),
    ("B", r"captured_0053", r"length of the book", 19.5, "white-covered book l"),
    ("B", r"captured_0053", r"width of the book", 12.5, "white-covered book w"),
    ("B", r"captured_0062", r"length of the white box", 19.5, "white food box l"),
    ("B", r"captured_0018", r"length of the box", 19.5, "white food box l"),
    # 0054: the "white ball" is named "pink ball" in 0054a's own question for the same event (pink tennis ball, 6.7)
    ("B", r"captured_0054", r"white ball's diameter", 6.7, "pink tennis ball d"),
    # 0013/0014 desk slope: the rolling ball is the pink tennis ball (frames)
    ("B", r"captured_001[34]", r"diameter of the ball", 6.7, "pink tennis ball d"),
]


def match(video_id, question):
    q = str(question).lower()
    for tier, fam, pat, val, name in RULES:
        if fam and not re.match(fam, str(video_id)):
            continue
        if re.search(pat, q):
            return tier, val, name
    return None
