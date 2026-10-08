"""Shared contract between question parsing, pixel measurement and the geometry solver.

Every QuantiPhy answer is "metric scale x pixel measurement". The pipeline is split so
that different sources (Claude, an open-weight VLM, a CV detector/tracker) can produce
the same intermediate records and one solver turns them into numbers:

    QuestionSpec   what to measure, from question + prior + depth text   (parsers)
    RoleTrack      where things are in pixels, frame by frame            (annotators / trackers)
    geometry.solve(spec, tracks, image_size) -> answer in the asked unit (qp/geometry.py)

Conventions
-----------
* Pixel coordinates are in the ORIGINAL video frame (x right, y down, origin top-left).
  Annotators that see resized frames must map back before writing a RoleTrack.
* Time `t` is in seconds, computed as frame_index / dataset_fps (the dataset's fps column,
  not the container fps).
* SI internally: metres, m/s, m/s^2. `QuestionSpec.target.unit` is the unit the question
  asks for; the solver converts the final SI value into it.
* Roles: "prior" (the object carrying the known quantity), "target" (the object asked
  about), "target2" (second object for distance-between-two-objects questions),
  "prior2" (second object when the prior is a distance between two objects).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Kind = Literal[
    "size",             # extent of one object (length/width/height/diameter/...), metres
    "distance",         # distance between two objects (or two points) at a time, metres
    "displacement",     # straight-line |p(t1) - p(t0)| of one object, metres
    "path_length",      # distance travelled along the trajectory between t0 and t1, metres
    "speed",            # magnitude of velocity at a time (or average over a window), m/s
    "acceleration",     # magnitude of acceleration at a time (or over a window), m/s^2
    "camera_distance",  # object-to-camera distance, metres (usually read from depth_info)
    "other",
]
KINDS: tuple[str, ...] = Kind.__args__  # type: ignore[attr-defined]

# Dimension of each kind: L (metres), V (m/s), A (m/s^2)
KIND_DIM = {
    "size": "L", "distance": "L", "displacement": "L", "path_length": "L",
    "camera_distance": "L", "speed": "V", "acceleration": "A", "other": "L",
}


@dataclass
class Quantity:
    kind: str                      # one of KINDS
    objects: list[str]             # short noun phrases, e.g. ["bird"]; two for "distance"
    dimension: str = ""            # for size: "length" | "height" | "width" | "diameter" | free text
    time: float | None = None      # instant in seconds (None = whole clip / not specified)
    window: list[float] | None = None  # [t0, t1] for displacement / path / average speed
    axis: str = "any"              # "any" | "horizontal" | "vertical" (e.g. free fall is vertical)
    value_si: float | None = None  # prior only: the known value in SI
    unit: str = ""                 # target only: unit asked for ("m", "cm", "m/s", "cm/s^2", ...)


@dataclass
class DepthEntry:
    object: str                    # object the distance refers to
    distance_m: float              # object-to-camera distance in metres
    time: float | None = None      # seconds; None = constant / unspecified


@dataclass
class QuestionSpec:
    qid: int
    target: Quantity
    prior: Quantity
    depth: list[DepthEntry] = field(default_factory=list)
    is_3d: bool = False            # video_type[1] == "3"
    notes: str = ""                # parser remarks (ambiguities), free text

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "QuestionSpec":
        return QuestionSpec(
            qid=int(d["qid"]),
            target=Quantity(**d["target"]),
            prior=Quantity(**d["prior"]),
            depth=[DepthEntry(**e) for e in d.get("depth", [])],
            is_3d=bool(d.get("is_3d", False)),
            notes=d.get("notes", ""),
        )


@dataclass
class Obs:
    """One object in one frame. Any field may be None if the source can't provide it."""
    t: float
    point: list[float] | None = None    # [x, y] consistent reference point (e.g. centre) for motion
    extent: list[list[float]] | None = None  # [[x1, y1], [x2, y2]] endpoints of the measured dimension
    box: list[float] | None = None      # [x1, y1, x2, y2] tight bounding box
    score: float | None = None          # source confidence in [0, 1]


@dataclass
class RoleTrack:
    role: str                      # "prior" | "prior2" | "target" | "target2"
    object: str
    obs: list[Obs]
    source: str = ""               # "claude", "qwen3vl", "owlv2+sam2", ...

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "RoleTrack":
        return RoleTrack(role=d["role"], object=d["object"], source=d.get("source", ""),
                         obs=[Obs(**o) for o in d["obs"]])


@dataclass
class Answer:
    qid: int
    value: float | None            # in the asked unit; None if unsolvable
    source: str                    # which pipeline produced it
    method: str = ""               # e.g. "2d_scale", "3d_focal_from_prior", "direct"
    flags: list[str] = field(default_factory=list)
    debug: dict = field(default_factory=dict)
