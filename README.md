# weight-transfer-and-balance-calculator


## What is this project?

I kept mixing up understeer and oversteer. I could recite the
definitions, but if someone asked me *why* a car does one or the other, I
didn't really have an answer beyond "something to do with weight
transfer." That wasn't good enough for me, so instead of re-reading the
explanation one more time, I decided to work through the calculation
myself and see if it actually clicked.

This is a small project — no real dataset, no telemetry, just the physics
worked out from first principles. It covers both directions a car's
weight can shift: front-to-back under braking, and side-to-side under
cornering.

## Why I built this

I wanted to actually understand what happens to a car's weight when it
brakes and when it corners, and why both of those matter for how grip
gets balanced between the tires. Not memorize the answer — calculate it
myself, so I'd know exactly where the numbers come from.

I started with just the braking side, but quickly realized that's only
half the story. Understeer and oversteer mostly show up *in corners*, not
in a straight line — so I went back and added the cornering side too,
since leaving it out would have left the same confusion only half solved.

## What I Found

**Braking (longitudinal) weight transfer** depends on mass, CG height,
braking force, and wheelbase. Braking hard at 1.2g shifted my example
car's front/rear split from a static 45/55 to roughly 58/42 — a bigger
shift than I expected before doing the maths.

**Cornering (lateral) weight transfer** works the same way, just rotated
90 degrees — track width takes the place of wheelbase, and cornering
force takes the place of braking force. Cornering hard at 1.5g shifted
weight from an even 50/50 left-right split to about 80/20 between the
outside and inside wheels. That's a much bigger swing than the braking
case, mostly because a typical track width is narrower than a wheelbase —
the same sideways force has less distance to act over, so it tips the
balance further.

**The piece that actually fixed my confusion:** lateral weight transfer
on its own only tells you how much weight moves to the outside wheels
overall — it doesn't say whether the front-outside or rear-outside tire
takes on more of that load. That split is controlled separately, by how
stiff the front suspension is compared to the rear (anti-roll bars and
springs). If the front is stiffer, the front axle carries more of the
lateral load relative to the rear, so the front tires run out of grip
first — that's understeer. If the rear is stiffer, it's the opposite —
the rear runs out of grip first, and that's oversteer. The basic weight
transfer numbers set the *overall* picture; the suspension stiffness
balance decides which end of the car actually feels it more.

See [Analysis.md](Analysis.md) for the full walkthrough.

## Tools

Python · NumPy · Matplotlib

