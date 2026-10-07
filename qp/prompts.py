"""Prompt builders. `direct` reproduces the official starter-kit zero-shot prompt;
`measure` asks the model to work in pixels and convert with the given prior, which the
paper suggests VLMs skip (they lean on world knowledge instead of the stated prior)."""

from __future__ import annotations

import pandas as pd

DIRECT_SYSTEM = (
    "You are an expert video analyst specializing in physics measurements.\n"
    "Analyze the video frames carefully and provide ONLY the numerical answer with units. "
    "No explanation or reasoning needed.\n"
    "Format your response as: [value] [unit]\n"
    "Example: 2.5 cm\n"
    "Be as accurate as possible with measurements and calculations. "
    "Please give me an estimated answer even if you are not sure."
)

MEASURE_SYSTEM = (
    "You are an expert in video-based physical measurement. You will see frames from one "
    "video, each labelled with its timestamp and pixel size, and one known physical quantity "
    "(the prior). Your answer must be derived from the frames and the prior, not from what "
    "such objects typically measure: the scene may be a simulation with unusual scales.\n\n"
    "Procedure:\n"
    "1. Identify the object the prior refers to and the object the question asks about.\n"
    "2. Measure the prior quantity in pixel units from the frames (pixels for a length; "
    "pixel displacement divided by elapsed time for a speed; change of speed over time for an "
    "acceleration). Use frames far apart in time for motion and give pixel coordinates.\n"
    "3. Derive the scale (metres per pixel) from step 2 and the prior. For 3D scenes, use the "
    "given camera distances: the scale grows in proportion to depth (pinhole camera).\n"
    "4. Measure the target in pixels the same way and convert it with the scale.\n"
    "5. Sanity-check the magnitude, then end with exactly one line:\n"
    "Final answer: <number> <unit>\n"
    "Use the unit the question asks for."
)


def context(row: pd.Series) -> str:
    """Prior + depth sentence, worded as in the official starter kit."""
    parts = []
    if isinstance(row.prior, str) and row.prior.strip():
        parts.append(f"Given that {row.prior.strip()}.")
    if row.depth_info.strip():
        parts.append("Additionally, you have the following information about the distance between "
                     f"the objects in the video and the shooting camera: {row.depth_info.strip()}")
    text = " ".join(parts)
    if text and text[-1] not in ".!?":
        text += "."
    return text + " " if text else ""


def build(method: str, row: pd.Series, n_frames: int, duration_s: float) -> tuple[str, str]:
    """Return (system_prompt, user_text)."""
    clip = f"The clip is {duration_s:.2f} s long at {row.fps:g} fps; {n_frames} frames are shown. "
    if method == "direct":
        return DIRECT_SYSTEM, (f"{clip}{context(row)}{row.question}\n\n"
                               "Please answer the question with numbers and units ONLY. No explanation needed.")
    if method == "measure":
        return MEASURE_SYSTEM, f"{clip}{context(row)}\nQuestion: {row.question}"
    raise ValueError(f"unknown method {method!r}")
