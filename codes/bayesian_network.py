"""
=====================================================================
  Super Mario AI Case Study
  Algorithm: Bayesian Network (Belief Estimation)
  Task:      Infer Hidden Threats Before Choosing Action
  Author:    Siddhant Kumar Singh  |  Roll No: 2024109296
=====================================================================

Narrative:
-----------
Mario approaches a partially hidden section of the level. He cannot
see everything: a Piranha Plant may emerge from a pipe, a Bullet Bill
launcher might be active, and a hidden block could contain a power-up.
Mario has only uncertain clues:
  - SoundCue   : whether he hears a warning sound
  - ScreenVisibility : whether the section is partially visible

He uses a Bayesian Network to estimate the probability of each hidden
threat BEFORE deciding whether to Advance, Wait, Jump, Retreat or
use a Power-Up. This separates BELIEF ESTIMATION from ACTION SELECTION.

Network Structure:
  SoundCue ─────────┐
                    v
  ScreenVis ──> [PipeThreat] ──> [LauncherActive]
                    │
                    v
               [HiddenPowerUp]

Variables (all binary: True / False):
  PipeThreat     : Piranha Plant about to emerge
  LauncherActive : Bullet Bill launcher is firing
  HiddenPowerUp  : block ahead contains a power-up
  SoundCue       : audible warning cue (observable)
  ScreenVis      : partial screen visibility (observable)

PEAS Description:
  Performance : Correctly estimate threat probability; avoid dying;
                collect power-up when safe
  Environment : Partially observable castle section
  Actuators   : Advance, Wait, Jump, Retreat, UsePowerUp
  Sensors     : SoundCue, ScreenVisibility

Task Environment Properties:
  Partially Observable | Stochastic | Sequential | Dynamic | Discrete | Single-Agent
=====================================================================
"""

# ─── Prior Probabilities ─────────────────────────────────────────
# P(PipeThreat)
P_pipe_threat = {True: 0.35, False: 0.65}

# P(LauncherActive | PipeThreat)
P_launcher_given_pipe = {
    True:  {True: 0.70, False: 0.30},   # launcher more likely when pipe threat present
    False: {True: 0.20, False: 0.80},
}

# P(HiddenPowerUp | PipeThreat)  — power-ups tend to appear near threats
P_powerup_given_pipe = {
    True:  {True: 0.55, False: 0.45},
    False: {True: 0.30, False: 0.70},
}

# P(SoundCue | PipeThreat)
P_sound_given_pipe = {
    True:  {True: 0.80, False: 0.20},
    False: {True: 0.25, False: 0.75},
}

# P(ScreenVis | PipeThreat)
P_screen_given_pipe = {
    True:  {True: 0.60, False: 0.40},
    False: {True: 0.40, False: 0.60},
}


# ─── Bayesian Update: P(PipeThreat | evidence) ──────────────────
def posterior_pipe_threat(sound_cue: bool, screen_vis: bool) -> dict:
    """
    Apply Bayes' Rule to update P(PipeThreat) given observed evidence.
    Evidence: SoundCue and ScreenVisibility
    """
    scores = {}
    for threat in [True, False]:
        prior       = P_pipe_threat[threat]
        likelihood_sound  = P_sound_given_pipe[threat][sound_cue]
        likelihood_screen = P_screen_given_pipe[threat][screen_vis]
        # Naively assume independence (simplified Bayesian net)
        scores[threat] = prior * likelihood_sound * likelihood_screen

    total = sum(scores.values())
    return {k: round(v / total, 4) for k, v in scores.items()}


def estimate_all(sound_cue: bool, screen_vis: bool) -> dict:
    """
    Given observed SoundCue and ScreenVisibility, estimate posterior
    probabilities for all hidden variables.
    """
    post_pipe = posterior_pipe_threat(sound_cue, screen_vis)
    
    # P(LauncherActive | evidence) = sum over PipeThreat
    p_launcher = {}
    for la in [True, False]:
        p_launcher[la] = sum(
            P_launcher_given_pipe[pipe][la] * post_pipe[pipe]
            for pipe in [True, False]
        )
    p_launcher = {k: round(v, 4) for k, v in p_launcher.items()}

    # P(HiddenPowerUp | evidence) = sum over PipeThreat
    p_powerup = {}
    for pu in [True, False]:
        p_powerup[pu] = sum(
            P_powerup_given_pipe[pipe][pu] * post_pipe[pipe]
            for pipe in [True, False]
        )
    p_powerup = {k: round(v, 4) for k, v in p_powerup.items()}

    return {
        "PipeThreat":     post_pipe,
        "LauncherActive": p_launcher,
        "HiddenPowerUp":  p_powerup,
    }


# ─── Display Helper ──────────────────────────────────────────────
def print_beliefs(beliefs: dict, sound_cue: bool, screen_vis: bool):
    print("\n" + "="*60)
    print("   Bayesian Network — Hidden Threat Estimation")
    print("="*60)
    print(f"   Evidence: SoundCue={sound_cue}, ScreenVisibility={screen_vis}")
    print("="*60)

    variables = {
        "PipeThreat":     "Piranha Plant Emerging from Pipe",
        "LauncherActive": "Bullet Bill Launcher is Active",
        "HiddenPowerUp":  "Block Contains Hidden Power-Up",
    }
    for var_key, description in variables.items():
        prob_true  = beliefs[var_key][True]
        prob_false = beliefs[var_key][False]
        bar_t = "#" * int(prob_true * 30)
        bar_f = "#" * int(prob_false * 30)
        print(f"\n  {description}")
        print(f"    P({var_key}=True ) = {prob_true:.4f}  [{bar_t:<30}]")
        print(f"    P({var_key}=False) = {prob_false:.4f}  [{bar_f:<30}]")

    print()


# ─── Scenario Comparison ─────────────────────────────────────────
def run_scenarios():
    scenarios = [
        {"sound": False, "screen": False, "label": "Quiet & No visibility"},
        {"sound": True,  "screen": False, "label": "Sound heard, no visibility"},
        {"sound": False, "screen": True,  "label": "Quiet but partial visibility"},
        {"sound": True,  "screen": True,  "label": "Sound + partial visibility"},
    ]

    print("\n" + "="*65)
    print("   BAYESIAN NETWORK — Super Mario Threat Estimation")
    print("   Author: Siddhant Kumar Singh  |  Roll: 2024109296")
    print("="*65)

    for sc in scenarios:
        beliefs = estimate_all(sc["sound"], sc["screen"])
        print(f"\n  === Scenario: {sc['label']} ===")
        print_beliefs(beliefs, sc["sound"], sc["screen"])

        # Risk advisory
        pipe_risk    = beliefs["PipeThreat"][True]
        launcher_risk = beliefs["LauncherActive"][True]
        powerup_chance = beliefs["HiddenPowerUp"][True]

        print(f"  Risk Assessment:")
        if pipe_risk > 0.6 or launcher_risk > 0.5:
            print(f"    => HIGH THREAT  (Pipe:{pipe_risk:.2f}, Launcher:{launcher_risk:.2f})")
            print(f"    => RECOMMENDATION: WAIT or RETREAT")
        elif powerup_chance > 0.4:
            print(f"    => Moderate threat but power-up likely ({powerup_chance:.2f})")
            print(f"    => RECOMMENDATION: JUMP carefully and grab power-up")
        else:
            print(f"    => LOW threat detected")
            print(f"    => RECOMMENDATION: ADVANCE")

    print("\n  Key Observations:")
    print("  * Bayesian Networks let Mario reason about UNSEEN threats.")
    print("  * A 20% threat of a lethal event may still require caution if consequence is death.")
    print("  * Both prior knowledge AND observed evidence update the belief state.")
    print("  * This inference feeds into the MDP for final action selection.\n")


if __name__ == "__main__":
    run_scenarios()
