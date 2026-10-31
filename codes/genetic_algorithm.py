"""
=====================================================================
  Super Mario AI Case Study
  Algorithm: Genetic Algorithm (GA)
  Task:      Evolve a High-Scoring Level-Completion Policy
  Author:    Siddhant Kumar Singh  |  Roll No: 2024109296
=====================================================================

Narrative:
-----------
Mario needs a reusable behaviour policy that works across several
level layouts. Each chromosome encodes behavioural weights such as:
  coin_attraction, powerup_attraction, enemy_avoidance,
  jump_aggressiveness, goal_urgency, retreat_tendency, open_space_pref

Different chromosomes represent different "Mario personalities".
A genetic algorithm evolves a population of these policies over
multiple generations, selecting fitter ones and applying crossover
and mutation to produce better generations.

PEAS Description:
  Performance : Level completion, coins collected, remaining lives,
                time taken, power-ups collected, survival rate
  Environment : Simulated Super Mario level with coins, enemies,
                power-ups, pipes, and a goal flag
  Actuators   : Behavioral weights that guide action selection
  Sensors     : Level state, coin/enemy/goal proximity

Task Environment Properties:
  Partially Observable | Stochastic | Sequential | Dynamic | Continuous | Single-Agent

Problem Formulation:
  Chromosome  : [coin_wt, powerup_wt, enemy_avoid_wt, jump_wt,
                 goal_urgency_wt, retreat_wt, open_space_wt]
  Each gene   : float in [0.0, 1.0]
  Fitness     : weighted combination of completion + coins +
                lives + speed - deaths
=====================================================================
"""

import random
import math

random.seed(42)

# ─── GA Hyper-parameters ────────────────────────────────────────
POPULATION_SIZE  = 20
CHROMOSOME_LEN   = 7          # number of behavioral genes
GENERATIONS      = 30
CROSSOVER_RATE   = 0.8
MUTATION_RATE    = 0.15
MUTATION_STRENGTH = 0.2       # max delta for mutation
TOURNAMENT_K     = 3          # tournament selection size
ELITISM_COUNT    = 2          # keep top N chromosomes unchanged

GENE_NAMES = [
    "CoinAttraction",
    "PowerUpAttraction",
    "EnemyAvoidance",
    "JumpAggressiveness",
    "GoalUrgency",
    "RetreatTendency",
    "OpenSpacePreference"
]


# ─── Fitness Simulation ──────────────────────────────────────────
def simulate_mario(chromosome):
    """
    Simplified simulator: evaluates a chromosome (behavioral policy)
    on a synthetic level and returns a fitness score.

    In a real implementation this would run actual game episodes.
    Here we use a mathematical model that captures the trade-offs:
      - High GoalUrgency + moderate EnemyAvoidance  → completion
      - High CoinAttraction alone  → many coins but frequent deaths
      - Very high JumpAggressiveness without open space → falls
    """
    coin_wt, powerup_wt, enemy_avoid_wt, jump_wt, goal_wt, retreat_wt, space_wt = chromosome

    # Completion probability: goal urgency helps, enemy avoidance helps,
    # excessive jumping without open-space awareness hurts
    completion_score = (
        0.5 * goal_wt
        + 0.3 * enemy_avoid_wt
        - 0.2 * max(0, jump_wt - space_wt)  # risky jumping penalty
        + 0.1 * retreat_wt
    )
    completion_score = max(0.0, min(1.0, completion_score))

    # Coins collected: coin attraction helps, but risk of death
    coins = coin_wt * 100 * (1 - 0.4 * (1 - enemy_avoid_wt))

    # Power-ups
    powerups = powerup_wt * 20

    # Survival: enemy avoidance and retreat tendency
    survival = (enemy_avoid_wt * 0.5 + retreat_wt * 0.3 + space_wt * 0.2) * 3

    # Time efficiency: goal urgency reduces time taken
    time_bonus = goal_wt * 50

    # Composite fitness
    fitness = (
        completion_score * 500
        + coins * 0.5
        + powerups * 2
        + survival * 30
        + time_bonus
    )
    return round(fitness, 2)


# ─── Population Initialisation ──────────────────────────────────
def init_population():
    return [
        [round(random.uniform(0.0, 1.0), 3) for _ in range(CHROMOSOME_LEN)]
        for _ in range(POPULATION_SIZE)
    ]


# ─── Selection: Tournament ───────────────────────────────────────
def tournament_select(population, fitnesses, k=TOURNAMENT_K):
    contenders = random.sample(list(zip(population, fitnesses)), k)
    winner = max(contenders, key=lambda x: x[1])
    return winner[0][:]


# ─── Crossover: Single-Point ─────────────────────────────────────
def crossover(parent1, parent2):
    if random.random() < CROSSOVER_RATE:
        point = random.randint(1, CHROMOSOME_LEN - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    return parent1[:], parent2[:]


# ─── Mutation: Gaussian Perturbation ────────────────────────────
def mutate(chromosome):
    for i in range(CHROMOSOME_LEN):
        if random.random() < MUTATION_RATE:
            delta = random.gauss(0, MUTATION_STRENGTH)
            chromosome[i] = round(max(0.0, min(1.0, chromosome[i] + delta)), 3)
    return chromosome


# ─── Main GA Loop ────────────────────────────────────────────────
def run_ga():
    population = init_population()
    best_fitness_history = []
    avg_fitness_history  = []

    print("\n" + "="*65)
    print("   Genetic Algorithm — Evolving Mario's Behaviour Policy")
    print("="*65)
    print(f"   Population: {POPULATION_SIZE}  |  Genes: {CHROMOSOME_LEN}  |  Generations: {GENERATIONS}")
    print(f"   Crossover rate: {CROSSOVER_RATE}  |  Mutation rate: {MUTATION_RATE}")
    print("="*65)
    print(f"\n{'Gen':>4}  {'Best Fitness':>13}  {'Avg Fitness':>12}  Best Chromosome (first 4 genes)")
    print("-"*65)

    best_ever_individual = None
    best_ever_fitness    = -math.inf

    for gen in range(1, GENERATIONS + 1):
        fitnesses = [simulate_mario(chromo) for chromo in population]

        gen_best_fit = max(fitnesses)
        gen_avg_fit  = round(sum(fitnesses) / len(fitnesses), 2)
        best_idx     = fitnesses.index(gen_best_fit)
        best_chromo  = population[best_idx]

        best_fitness_history.append(gen_best_fit)
        avg_fitness_history.append(gen_avg_fit)

        if gen_best_fit > best_ever_fitness:
            best_ever_fitness    = gen_best_fit
            best_ever_individual = best_chromo[:]

        genes_preview = [f"{v:.2f}" for v in best_chromo[:4]]
        print(f"{gen:>4}  {gen_best_fit:>13.2f}  {gen_avg_fit:>12.2f}  {genes_preview}")

        # Elitism: carry top N into next generation unchanged
        sorted_pop = sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)
        next_population = [ind for _, ind in sorted_pop[:ELITISM_COUNT]]

        # Fill rest via selection → crossover → mutation
        while len(next_population) < POPULATION_SIZE:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)
            c1, c2 = crossover(p1, p2)
            next_population.append(mutate(c1))
            if len(next_population) < POPULATION_SIZE:
                next_population.append(mutate(c2))

        population = next_population

    # ── Final Report ─────────────────────────────────────────────
    print("\n" + "="*65)
    print("   EVOLUTION COMPLETE")
    print("="*65)
    print(f"   Best Fitness Achieved : {best_ever_fitness:.2f}")
    print(f"\n   Best Mario Policy (Chromosome):")
    for name, val in zip(GENE_NAMES, best_ever_individual):
        bar = "#" * int(val * 20)
        print(f"     {name:<24}: {val:.3f}  [{bar:<20}]")

    print("\n   Fitness Progression (first 10 generations):")
    print(f"   {'Gen':>4}  {'Best':>10}  {'Avg':>10}")
    for i, (b, a) in enumerate(zip(best_fitness_history[:10],
                                   avg_fitness_history[:10]), 1):
        print(f"   {i:>4}  {b:>10.2f}  {a:>10.2f}")

    print("\n  Key Observations:")
    print("  * Chromosomes with BALANCED goal urgency + enemy avoidance score highest.")
    print("  * Pure coin attraction (high CoinAttraction, low GoalUrgency) plateaus early.")
    print("  * Mutation prevents premature convergence; elitism preserves best solutions.")
    print("  * Fitness function design is CRITICAL—wrong weights reward undesired behaviour.")
    print("  * Time Complexity: O(G * P * F) where G=generations, P=population, F=fitness eval\n")

    return best_ever_individual, best_ever_fitness


if __name__ == "__main__":
    run_ga()
