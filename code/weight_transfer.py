"""
Weight Transfer & Balance Calculator
A simple vehicle dynamics project: no external data, just physics.

This covers BOTH directions weight can shift in a car:
  - LONGITUDINAL: front <-> rear, caused by braking/accelerating
  - LATERAL: left <-> right (inside <-> outside), caused by cornering

Together these explain the basic mechanism behind understeer and
oversteer, and why brake bias and anti-roll bar settings matter.
"""

import numpy as np
import matplotlib.pyplot as plt

GRAVITY = 9.81  # m/s^2

# =====================================================================
# CAR PARAMETERS (estimated, representative values for a small
# single-seater - not measured from a real car)
# =====================================================================

MASS_KG = 730                  # total car mass (kg)
STATIC_FRONT_PERCENT = 45.0    # % of weight on the front axle at rest
WHEELBASE_M = 2.7              # distance between front and rear axles (m)
TRACK_WIDTH_M = 1.5            # distance between left and right wheels (m)
CG_HEIGHT_M = 0.30             # height of center of gravity above ground (m)


# =====================================================================
# PART A — LONGITUDINAL WEIGHT TRANSFER (braking / accelerating)
#
#   weight_transfer = (mass * accel_g * CG_height) / wheelbase
#
# Positive accel_g = braking (weight moves to FRONT)
# Negative accel_g = accelerating (weight moves to REAR)
# =====================================================================

def longitudinal_weight_transfer_kg(mass_kg, accel_g, cg_height_m, wheelbase_m):
    accel_ms2 = accel_g * GRAVITY
    transfer_n = (mass_kg * accel_ms2 * cg_height_m) / wheelbase_m
    return transfer_n / GRAVITY


def dynamic_front_rear_split(mass_kg, static_front_percent, accel_g,
                              cg_height_m, wheelbase_m):
    static_front = mass_kg * (static_front_percent / 100)
    static_rear = mass_kg - static_front

    transfer = longitudinal_weight_transfer_kg(mass_kg, accel_g, cg_height_m, wheelbase_m)

    dynamic_front = static_front + transfer
    dynamic_rear = static_rear - transfer
    dynamic_front_percent = (dynamic_front / mass_kg) * 100

    return {
        'static_front_kg': static_front,
        'static_rear_kg': static_rear,
        'transfer_kg': transfer,
        'dynamic_front_kg': dynamic_front,
        'dynamic_rear_kg': dynamic_rear,
        'dynamic_front_percent': dynamic_front_percent
    }


# =====================================================================
# PART B — LATERAL WEIGHT TRANSFER (cornering)
#
# Same shape of formula, but rotated 90 degrees: TRACK WIDTH replaces
# wheelbase, and LATERAL g (cornering force) replaces braking g.
#
#   weight_transfer = (mass * lateral_g * CG_height) / track_width
#
# This is the weight that moves from the INSIDE wheels to the OUTSIDE
# wheels during a corner. At rest (no cornering), left/right split is
# assumed even (50/50) - most cars are roughly symmetric side to side.
# =====================================================================

def lateral_weight_transfer_kg(mass_kg, lateral_g, cg_height_m, track_width_m):
    lateral_ms2 = lateral_g * GRAVITY
    transfer_n = (mass_kg * lateral_ms2 * cg_height_m) / track_width_m
    return transfer_n / GRAVITY


def dynamic_inside_outside_split(mass_kg, lateral_g, cg_height_m, track_width_m):
    static_each_side = mass_kg / 2  # assume even left/right split at rest

    transfer = lateral_weight_transfer_kg(mass_kg, lateral_g, cg_height_m, track_width_m)

    dynamic_outside = static_each_side + transfer
    dynamic_inside = static_each_side - transfer
    dynamic_outside_percent = (dynamic_outside / mass_kg) * 100

    return {
        'static_each_side_kg': static_each_side,
        'transfer_kg': transfer,
        'dynamic_outside_kg': dynamic_outside,
        'dynamic_inside_kg': dynamic_inside,
        'dynamic_outside_percent': dynamic_outside_percent
    }


# =====================================================================
# PART C — COMBINING BOTH: WHY FRONT/REAR BALANCE MATTERS UNDER CORNERING
#
# Lateral weight transfer tells you how much weight moves to the
# outside wheels overall - but it doesn't by itself say whether the
# FRONT-outside or REAR-outside tire takes on more of that load. That
# split is controlled by suspension stiffness balance (anti-roll bars,
# springs), not by the basic formula above.
#
# A simple way to represent this without modeling full suspension:
# a "front lateral load share" - what fraction of the total lateral
# weight transfer is being carried by the front axle vs the rear axle.
# A higher front share means the front tires are working harder
# relative to the rear during cornering.
# =====================================================================

def front_rear_lateral_load_share(total_lateral_transfer_kg, front_share_percent):
    front_lateral_kg = total_lateral_transfer_kg * (front_share_percent / 100)
    rear_lateral_kg = total_lateral_transfer_kg - front_lateral_kg
    return front_lateral_kg, rear_lateral_kg


# =====================================================================
# EXAMPLE CALCULATIONS
# =====================================================================

print("=== Static Weight Distribution ===")
static_front = MASS_KG * (STATIC_FRONT_PERCENT / 100)
print(f"Total mass: {MASS_KG} kg")
print(f"Static front/rear split: {STATIC_FRONT_PERCENT:.1f}% / {100-STATIC_FRONT_PERCENT:.1f}%")
print(f"Static left/right split: 50.0% / 50.0% (assumed symmetric)")

print("\n=== PART A: Longitudinal Weight Transfer (braking at 1.2g) ===")
longitudinal = dynamic_front_rear_split(MASS_KG, STATIC_FRONT_PERCENT, 1.2,
                                          CG_HEIGHT_M, WHEELBASE_M)
print(f"Weight transferred to front: {longitudinal['transfer_kg']:.1f} kg")
print(f"Dynamic front/rear split: {longitudinal['dynamic_front_percent']:.1f}% / "
      f"{100-longitudinal['dynamic_front_percent']:.1f}%")

print("\n=== PART B: Lateral Weight Transfer (cornering at 1.5g) ===")
lateral = dynamic_inside_outside_split(MASS_KG, 1.5, CG_HEIGHT_M, TRACK_WIDTH_M)
print(f"Weight transferred to outside wheels: {lateral['transfer_kg']:.1f} kg")
print(f"Dynamic outside/inside split: {lateral['dynamic_outside_percent']:.1f}% / "
      f"{100-lateral['dynamic_outside_percent']:.1f}%")

print("\n=== PART C: Front vs Rear Share of That Lateral Transfer ===")
print("(this is what anti-roll bar / spring stiffness balance actually controls)")
for front_share in [40, 50, 60, 70]:
    front_kg, rear_kg = front_rear_lateral_load_share(lateral['transfer_kg'], front_share)
    tendency = "more understeer-prone" if front_share > 50 else \
               "more oversteer-prone" if front_share < 50 else "neutral"
    print(f"  Front share {front_share}%: front axle carries {front_kg:.1f} kg, "
          f"rear axle carries {rear_kg:.1f} kg of the lateral transfer -> {tendency}")


# =====================================================================
# SENSITIVITY SWEEPS
# =====================================================================

# --- Sweep 1: longitudinal bias vs braking force ---
decel_range = np.linspace(0.2, 1.5, 30)
bias_vs_decel = [dynamic_front_rear_split(MASS_KG, STATIC_FRONT_PERCENT, d,
                                            CG_HEIGHT_M, WHEELBASE_M)['dynamic_front_percent']
                  for d in decel_range]

# --- Sweep 2: lateral transfer vs cornering force ---
lat_g_range = np.linspace(0.2, 2.0, 30)
lateral_transfer_vs_g = [dynamic_inside_outside_split(MASS_KG, g, CG_HEIGHT_M,
                                                         TRACK_WIDTH_M)['dynamic_outside_percent']
                           for g in lat_g_range]

# --- Sweep 3: lateral transfer vs CG height (cornering fixed at 1.5g) ---
cg_range = np.linspace(0.20, 0.45, 30)
lateral_transfer_vs_cg = [dynamic_inside_outside_split(MASS_KG, 1.5, c,
                                                          TRACK_WIDTH_M)['dynamic_outside_percent']
                            for c in cg_range]

# --- Sweep 4: lateral transfer vs track width (cornering fixed at 1.5g) ---
track_range = np.linspace(1.2, 1.9, 30)
lateral_transfer_vs_track = [dynamic_inside_outside_split(MASS_KG, 1.5, CG_HEIGHT_M,
                                                             t)['dynamic_outside_percent']
                               for t in track_range]


# =====================================================================
# PLOTS
# =====================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].plot(decel_range, bias_vs_decel, color='steelblue', linewidth=2)
axes[0, 0].axhline(STATIC_FRONT_PERCENT, color='gray', linestyle='--', label='Static front %')
axes[0, 0].set_xlabel("Braking Deceleration (g)")
axes[0, 0].set_ylabel("Dynamic Front Weight (%)")
axes[0, 0].set_title("Longitudinal: Front Weight vs Braking Force")
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

axes[0, 1].plot(lat_g_range, lateral_transfer_vs_g, color='darkorange', linewidth=2)
axes[0, 1].axhline(50.0, color='gray', linestyle='--', label='Static 50/50')
axes[0, 1].set_xlabel("Lateral (Cornering) g")
axes[0, 1].set_ylabel("Dynamic Outside Weight (%)")
axes[0, 1].set_title("Lateral: Outside Weight vs Cornering Force")
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

axes[1, 0].plot(cg_range, lateral_transfer_vs_cg, color='seagreen', linewidth=2)
axes[1, 0].axhline(50.0, color='gray', linestyle='--', label='Static 50/50')
axes[1, 0].set_xlabel("CG Height (m)")
axes[1, 0].set_ylabel("Dynamic Outside Weight (%)")
axes[1, 0].set_title("Lateral: Outside Weight vs CG Height (at 1.5g cornering)")
axes[1, 0].legend()
axes[1, 0].grid(alpha=0.3)

axes[1, 1].plot(track_range, lateral_transfer_vs_track, color='indianred', linewidth=2)
axes[1, 1].axhline(50.0, color='gray', linestyle='--', label='Static 50/50')
axes[1, 1].set_xlabel("Track Width (m)")
axes[1, 1].set_ylabel("Dynamic Outside Weight (%)")
axes[1, 1].set_title("Lateral: Outside Weight vs Track Width (at 1.5g cornering)")
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("weight_transfer_combined.png", dpi=150)
plt.show()

print("\nSaved weight_transfer_combined.png")