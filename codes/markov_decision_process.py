"""
=====================================================================
  Super Mario AI Case Study
  Algorithm: Markov Decision Process (MDP) + Value Iteration
  Task:      Choose the Best Action Given Threat Belief State
  Author:    Siddhant Kumar Singh  |  Roll No: 2024109296
=====================================================================

Narrative:
-----------
After the Bayesian Network estimates threat probabilities, Mario must
DECIDE what to do next. This is where the MDP takes over.

States represent Mario's combined situation:
  danger_level  : LOW / MEDIUM / HIGH
  powerup_status: HAS_POWERUP / NO_POWERUP
  location      : SAFE_ZONE / NEAR_PIPE / NEAR_LAUNCHER

Actions available:
  ADVANCE, WAIT, JUMP, RETREAT, USE_POWERUP

The MDP captures:
  - Transition probabilities T(s, a, s')
  - Reward function R(s, a, s')
  - Discount factor gamma (future reward weight)

Value Iteration finds the optimal value V*(s) for each state,
from which we derive the optimal policy pi*(s) = best action at state s.

PEAS Description:
  Performance : Maximize long-term survival + progress + item collection
  Environment : Partially observable castle section (belief-state driven)
  Actuators   : ADVANCE, WAIT, JUMP, RETREAT, USE_POWERUP
  Sensors     : Danger level, power-up status, location

Task Environment Properties:
  Partially Observable | Stochastic | Sequential | Dynamic | Discrete | Single-Agent

Problem Formulation:
  S  = {(danger, powerup, location)} — finite state set
  A  = {ADVANCE, WAIT, JUMP, RETREAT, USE_POWERUP}
  T  = T(s, a, s') — transition probabilities
  R  = R(s, a, s') — immediate rewards
  gamma = 0.9 — discount factor
  Goal: find pi*(s) = argmax_a [R + gamma * sum(T * V(s'))]
=====================================================================
"""

# ─── State and Action Definitions ───────────────────────────────
DANGER   = ["LOW", "MEDIUM", "HIGH"]
POWERUP  = ["HAS_POWERUP", "NO_POWERUP"]
LOCATION = ["SAFE_ZONE", "NEAR_PIPE", "NEAR_LAUNCHER"]
ACTIONS  = ["ADVANCE", "WAIT", "JUMP", "RETREAT", "USE_POWERUP"]

# Build full state space
STATES = [(d, p, l) for d in DANGER for p in POWERUP for l in LOCATION]
STATE_INDEX = {s: i for i, s in enumerate(STATES)}

GAMMA    = 0.90
THETA    = 1e-6        # convergence threshold for value iteration
MAX_ITER = 1000


# ─── Transition Model T(s, a) → list of (prob, next_state, reward) ──
def get_transitions(state, action):
    """
    Returns a list of (probability, next_state, reward) tuples.
    Models the uncertain outcomes of each action.
    """
    danger, powerup, location = state
    transitions = []

    if action == "ADVANCE":
        if danger == "LOW":
            # 85% success: move to SAFE_ZONE
            transitions.append((0.85, ("LOW",    powerup, "SAFE_ZONE"),    +10))
            transitions.append((0.10, ("MEDIUM", powerup, "NEAR_PIPE"),    -5))
            transitions.append((0.05, ("HIGH",   powerup, "NEAR_LAUNCHER"),-15))
        elif danger == "MEDIUM":
            transitions.append((0.60, ("LOW",    powerup, "SAFE_ZONE"),    +8))
            transitions.append((0.25, ("MEDIUM", powerup, location),       -3))
            transitions.append((0.15, ("HIGH",   powerup, "NEAR_LAUNCHER"),-20))
        else:  # HIGH danger
            transitions.append((0.30, ("MEDIUM", powerup, "SAFE_ZONE"),    +5))
            transitions.append((0.40, ("HIGH",   powerup, location),       -20))
            transitions.append((0.30, ("HIGH",   powerup, "NEAR_LAUNCHER"),-40))  # death risk

    elif action == "WAIT":
        # Waiting reduces danger but costs time
        if danger == "HIGH":
            transitions.append((0.70, ("MEDIUM", powerup, location),      -2))
            transitions.append((0.30, ("HIGH",   powerup, location),      -5))
        elif danger == "MEDIUM":
            transitions.append((0.80, ("LOW",    powerup, location),      -1))
            transitions.append((0.20, ("MEDIUM", powerup, location),      -3))
        else:
            transitions.append((1.00, ("LOW",    powerup, location),      -1))

    elif action == "JUMP":
        if location in ("NEAR_PIPE", "NEAR_LAUNCHER"):
            # Jumping over threats
            if danger == "LOW":
                transitions.append((0.90, ("LOW",    powerup, "SAFE_ZONE"),   +12))
                transitions.append((0.10, ("MEDIUM", powerup, location),      -8))
            elif danger == "MEDIUM":
                transitions.append((0.60, ("LOW",    powerup, "SAFE_ZONE"),   +10))
                transitions.append((0.40, ("HIGH",   powerup, location),      -18))
            else:
                transitions.append((0.35, ("MEDIUM", powerup, "SAFE_ZONE"),   +6))
                transitions.append((0.65, ("HIGH",   powerup, location),      -30))
        else:  # SAFE_ZONE jump
            transitions.append((0.95, ("LOW",    powerup, "SAFE_ZONE"),   +3))
            transitions.append((0.05, ("MEDIUM", powerup, location),      -4))

    elif action == "RETREAT":
        # Moving back is always safer but reduces progress
        transitions.append((0.90, ("LOW",    powerup, "SAFE_ZONE"),   -8))
        transitions.append((0.10, ("MEDIUM", powerup, "SAFE_ZONE"),   -10))

    elif action == "USE_POWERUP":
        if powerup == "HAS_POWERUP":
            # Power-up reduces danger significantly
            if danger == "HIGH":
                transitions.append((0.85, ("LOW",    "NO_POWERUP", location),  +20))
                transitions.append((0.15, ("MEDIUM", "NO_POWERUP", location),  +5))
            elif danger == "MEDIUM":
                transitions.append((0.90, ("LOW",    "NO_POWERUP", location),  +15))
                transitions.append((0.10, ("LOW",    "NO_POWERUP", "SAFE_ZONE"),+10))
            else:
                transitions.append((1.00, ("LOW",    "NO_POWERUP", location),  +5))
        else:
            # No power-up: wasted action
            transitions.append((1.00, state, -5))

    if not transitions:
        transitions.append((1.00, state, -1))

    return transitions


# ─── Value Iteration ─────────────────────────────────────────────
def value_iteration():
    V      = {s: 0.0 for s in STATES}
    policy = {s: ACTIONS[0] for s in STATES}

    print("\n" + "="*65)
    print("   MDP Value Iteration — Optimal Action Policy for Mario")
    print("="*65)
    print(f"   States  : {len(STATES)}")
    print(f"   Actions : {ACTIONS}")
    print(f"   Gamma   : {GAMMA}  |  Convergence threshold: {THETA}")
    print("="*65)

    for iteration in range(MAX_ITER):
        delta  = 0.0
        V_new  = {}

        for state in STATES:
            action_values = {}
            for action in ACTIONS:
                trans = get_transitions(state, action)
                q_value = sum(
                    prob * (reward + GAMMA * V[next_s])
                    for prob, next_s, reward in trans
                )
                action_values[action] = round(q_value, 4)

            best_action = max(action_values, key=action_values.get)
            best_value  = action_values[best_action]
            V_new[state]    = best_value
            policy[state]   = best_action
            delta = max(delta, abs(best_value - V[state]))

        V = V_new

        if (iteration + 1) % 50 == 0 or delta < THETA:
            print(f"   Iteration {iteration+1:>4} | Max delta: {delta:.8f}")

        if delta < THETA:
            print(f"\n   Converged after {iteration+1} iterations.")
            break

    return V, policy


# ─── Display Policy ──────────────────────────────────────────────
def display_policy(V, policy):
    print("\n" + "="*65)
    print("   Optimal Policy pi*(s)  — What Mario Should Do")
    print("="*65)
    print(f"  {'State (Danger|PowerUp|Location)':<42} {'Action':<14} {'V*(s)':>8}")
    print("-"*65)

    for state in STATES:
        d, p, l = state
        state_str = f"{d}|{p}|{l}"
        print(f"  {state_str:<42} {policy[state]:<14} {V[state]:>8.2f}")


# ─── Query: Recommend Action for Specific Belief ─────────────────
def recommend_action(danger: str, powerup: str, location: str, V: dict, policy: dict):
    state = (danger, powerup, location)
    if state not in policy:
        print("  Unknown state.")
        return
    action = policy[state]
    value  = V[state]
    print(f"\n  Query: Danger={danger}, PowerUp={powerup}, Location={location}")
    print(f"  Recommended Action : {action}")
    print(f"  Expected Long-term Value : {value:.2f}")

    # Show all Q-values for this state
    trans_by_action = {}
    for a in ACTIONS:
        trans = get_transitions(state, a)
        q = sum(prob * (reward + GAMMA * V[ns]) for prob, ns, reward in trans)
        trans_by_action[a] = round(q, 2)

    print(f"\n  Q-values for this state:")
    for a, q in sorted(trans_by_action.items(), key=lambda x: -x[1]):
        bar = "#" * max(0, int((q + 30) * 0.5))
        marker = " <== OPTIMAL" if a == action else ""
        print(f"    {a:<15}: {q:>8.2f}{marker}")


# ─── Main ─────────────────────────────────────────────────────────
def main():
    V, policy = value_iteration()
    display_policy(V, policy)

    print("\n" + "="*65)
    print("   Scenario-Based Action Recommendations")
    print("="*65)

    recommend_action("HIGH",   "HAS_POWERUP", "NEAR_PIPE",     V, policy)
    recommend_action("HIGH",   "NO_POWERUP",  "NEAR_LAUNCHER", V, policy)
    recommend_action("MEDIUM", "HAS_POWERUP", "NEAR_PIPE",     V, policy)
    recommend_action("LOW",    "NO_POWERUP",  "SAFE_ZONE",     V, policy)
    recommend_action("HIGH",   "NO_POWERUP",  "NEAR_PIPE",     V, policy)

    print("\n  Key Observations:")
    print("  * MDP rewards long-term EXPECTED return, not just immediate gain.")
    print("  * High-danger states with no power-up → RETREAT or WAIT is optimal.")
    print("  * USE_POWERUP has highest value in HIGH-danger states when power-up available.")
    print("  * Discount factor gamma controls how much future rewards matter.")
    print("  * The Bellman Equation underpins each value update: V(s) = max_a[R + γ Σ T*V(s')]")
    print("  * Time Complexity: O(iterations * |S| * |A| * |S|)\n")


if __name__ == "__main__":
    main()
