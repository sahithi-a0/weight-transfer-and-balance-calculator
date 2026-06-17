# Analysis Walkthrough
## Why I Started Here

The honest trigger: I kept confusing understeer and oversteer. I could
recite the definitions, but if someone asked me *why* a car does one or
the other, I didn't have a real answer beyond "weight transfer, somehow."
So instead of reading the explanation again, I decided to build the
calculation myself.

A note on the numbers I used: I don't have access to a real car's mass,
CG height, wheelbase, or track width — these are internal engineering
specs, not something you can pull from timing data. So everywhere in this
project I used reasonable, representative estimates for a small
single-seater, not measured values. The goal was understanding the
relationship, not modeling one specific real car.

---

## Part A — Longitudinal Weight Transfer (Braking)

When a car brakes, weight shifts forward — the same reason you get pushed
into your seatbelt under hard braking. The car's mass wants to keep
moving forward (inertia), which creates an effective forward weight shift
onto the front tires.

```
weight_transfer = (mass × braking_g × CG_height) / wheelbase
```

A heavier car transfers more weight. Braking harder transfers more
weight. And a car with a higher center of gravity transfers more weight
too, because the braking force acts through a taller "lever arm" above
the wheels.

For my example car (730 kg, 45/55 static front/rear split), braking at
1.2g shifted about 97 kg from the rear to the front — moving the split
from 45/55 to roughly 58/42. Bigger than I expected before calculating it
properly.

This explains why brake bias needs to shift forward under hard braking:
the front tires are carrying more load, so they can handle more braking
force before locking up. Real setups bias slightly more rearward than
this theoretical ideal, because locking the front (the car goes straight,
recoverable) is a safer mistake than locking the rear (the car spins).

---

## Part B — Lateral Weight Transfer (Cornering)

This is the half I hadn't touched at first, and it's the half that
actually matters most for understeer and oversteer, since both mostly
show up in corners, not in a straight line.

The formula has exactly the same shape as the braking case, just rotated
90 degrees:

```
weight_transfer = (mass × lateral_g × CG_height) / track_width
```

**Track width** (the distance between the left and right wheels) replaces
wheelbase, and **lateral g** (cornering force) replaces braking g. The car
isn't pitching forward and back anymore — it's rolling side to side, and
weight moves from the inside wheels to the outside wheels.

For my example car, cornering at 1.5g shifted about 219 kg onto the
outside wheels — moving the left/right split from an even 50/50 to
roughly 80/20. That's a much bigger swing than the braking case produced,
and the reason makes sense once I thought about it: track width (1.5m in
my example) is narrower than wheelbase (2.7m), so the same kind of
sideways force has less distance to act over, which tips the balance
further for the same CG height.

---

## Part C — The Piece That Actually Fixed My Confusion

Here's where it clicked. Lateral weight transfer tells you the *total*
amount of weight that moves to the outside wheels during a corner — but
it doesn't say whether the front-outside tire or the rear-outside tire
ends up carrying more of that load. That split isn't decided by the basic
weight transfer formula at all — it's decided by how stiff the front
suspension is compared to the rear (anti-roll bars and springs).

I modeled this as a simple "front lateral load share" — what percentage
of the total lateral transfer the front axle ends up carrying:

- **50% share:** front and rear split the lateral load evenly — neutral
  balance.
- **Above 50% (stiffer front):** the front axle carries more of the
  lateral load relative to the rear. The front tires are working harder,
  closer to their grip limit, so they run out of grip first in a corner.
  That's **understeer**.
- **Below 50% (stiffer rear):** the rear axle carries more of the lateral
  load. The rear tires run out of grip first. That's **oversteer**.

This is the sentence I could not have explained confidently before
building this: understeer and oversteer aren't really about *how much*
weight transfers sideways — that's mostly fixed by the car's mass, CG
height, and track width. They're about *which end of the car* ends up
carrying more of that transferred weight, which is a suspension stiffness
balance decision, layered on top of the basic weight transfer physics.

---

## Sensitivity Sweeps

I tested how lateral weight transfer responds to a few different things:

**Cornering force.** From a gentle 0.2g corner to a hard 2.0g corner, the
outside-wheel weight share climbed from about 54% to nearly 90%. The
harder you corner, the more lopsided the weight distribution gets.

**CG height.** At a fixed 1.5g corner, raising CG height from 0.20m to
0.45m pushed the outside-wheel share from about 70% to 95%. Same
relationship as the braking case — a taller car transfers more weight,
in either direction.

**Track width.** At a fixed 1.5g corner, widening the track from 1.2m to
1.9m brought the outside-wheel share down from about 87% to 74%. This is
the one new relationship I hadn't seen in the braking case — a wider
stance resists lateral weight transfer, which is part of why race cars
are built as wide as the regulations allow.



All four relationships came out as smooth, predictable curves, which
matched what the formulas suggested — but actually seeing it plotted out,
side by side for both directions, made the symmetry between braking and
cornering weight transfer click in a way that just reading the equations
didn't.

---

## What I Actually Learned

This project didn't involve anything advanced — it's basic mechanics in
two directions instead of one. But it took a concept I could only gesture
at vaguely (weight transfer, understeer, oversteer) and turned it into
something I can calculate, plot, and explain properly — including the
part I was originally missing, which is that suspension balance, not just
raw weight transfer, is what actually decides which end of the car loses
grip first. If I come back to this in a few months and feel that old
confusion creeping back, this is exactly where I'll come to re-derive it
from scratch.

---

## Limitations & Honesty Check

- Mass, CG height, wheelbase, track width, and static weight split are
  estimated, representative values for a small single-seater — not
  measured from a real car or pulled from any dataset.
- Both models treat braking/cornering as a single steady value. In a
  real corner, especially while trail-braking, longitudinal and lateral
  forces happen at the same time and interact — this project treats them
  separately, one at a time.
- The "front lateral load share" used in Part C is a simplified
  stand-in for how anti-roll bars and spring stiffness actually distribute
  load — a full suspension model would calculate this from real spring
  rates and roll stiffness rather than an assumed percentage.
- The left/right static split is assumed to be a perfectly even 50/50.
  Real cars can have small left/right asymmetries (driver weight,
  component placement) that this project doesn't account for.
- This project models weight transfer as the underlying cause of grip
  balance, but tire grip itself also depends on tire temperature,
  pressure, and surface — all held constant and ignored here, since the
  goal was isolating the weight transfer mechanism on its own.
