# internet_0040 - credit card held by a hand, moving up and to the left (static camera, 28 frames)
- Card pixel extents at frame 22 (where the card is still): horizontal 423 px (left x~941, right x~1364, the thumb covers part of the right edge), vertical 287 px. Ratio 1.47 (an ISO card is 1.586, so the card is slightly foreshortened).
- The prior "width = 83.98 mm" is most likely a typo for the ISO width of 53.98 mm. 83.98 mm cannot be the short side: the long side would then be about 123 mm.
- 3051 length: the ISO length is 85.6 mm. Answer 8.4 cm, leaning toward 8.56. If the prior is instead read as the horizontal size, the vertical size would be 5.7 cm. Confidence: medium-low.
- 3052 displacement: template match of the chip, text and numbers region. Centre at frame 0 = (1461,2612) and at frame 22 = (1110,2070), so the card moved 646 px. Converting with each candidate scale (0.188, 0.1985 or 0.202 mm/px) gives 12.1 to 13.1 cm. Answer 12.6 cm. Confidence: medium-high.
- 3053 speed: 12.6 cm / 0.733 s = 17.2 cm/s, treated as average speed over the interval. Confidence: medium.
