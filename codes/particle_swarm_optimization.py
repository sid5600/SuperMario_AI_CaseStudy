"""
Super Mario AI Case Study
Algorithm: Particle Swarm Optimization (PSO)
Task: Tune Mario's behavioral policy weights.
Author: Siddhant Kumar Singh | Roll No: 2024109296
"""

import random

random.seed(42)

DIMENSIONS = 7
PARTICLES = 20
ITERATIONS = 30
INERTIA = 0.7
COGNITIVE = 1.4
SOCIAL = 1.4
NAMES = [
    "CoinAttraction",
    "PowerUpAttraction",
    "EnemyAvoidance",
    "JumpAggressiveness",
    "GoalUrgency",
    "RetreatTendency",
    "OpenSpacePreference",
]


def fitness(position):
    coin, powerup, avoid, jump, goal, retreat, space = position
    completion = max(0.0, min(1.0, 0.5 * goal + 0.3 * avoid
                               - 0.2 * max(0.0, jump - space)
                               + 0.1 * retreat))
    coins = coin * 100 * (1 - 0.4 * (1 - avoid))
    survival = (avoid * 0.5 + retreat * 0.3 + space * 0.2) * 3
    return round(completion * 500 + coins * 0.5 + powerup * 40
                 + survival * 30 + goal * 50, 2)


def run_pso():
    positions = [[random.random() for _ in range(DIMENSIONS)]
                 for _ in range(PARTICLES)]
    velocities = [[random.uniform(-0.1, 0.1) for _ in range(DIMENSIONS)]
                  for _ in range(PARTICLES)]
    personal_best = [particle[:] for particle in positions]
    personal_scores = [fitness(particle) for particle in positions]
    best_index = max(range(PARTICLES), key=personal_scores.__getitem__)
    global_best = personal_best[best_index][:]
    global_score = personal_scores[best_index]

    for _ in range(ITERATIONS):
        for i, particle in enumerate(positions):
            for d in range(DIMENSIONS):
                r1, r2 = random.random(), random.random()
                velocities[i][d] = (
                    INERTIA * velocities[i][d]
                    + COGNITIVE * r1 * (personal_best[i][d] - particle[d])
                    + SOCIAL * r2 * (global_best[d] - particle[d])
                )
                particle[d] = max(0.0, min(1.0, particle[d] + velocities[i][d]))

            score = fitness(particle)
            if score > personal_scores[i]:
                personal_best[i] = particle[:]
                personal_scores[i] = score
                if score > global_score:
                    global_best = particle[:]
                    global_score = score

    return global_best, global_score


def main():
    best_policy, score = run_pso()
    print("Particle Swarm Optimization — Tuning Mario's Policy")
    print(f"Particles: {PARTICLES} | Iterations: {ITERATIONS}")
    print(f"Best fitness: {score:.2f}")
    for name, value in zip(NAMES, best_policy):
        print(f"{name:<22}: {value:.3f}")


if __name__ == "__main__":
    main()
