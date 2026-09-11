#!/usr/bin/env python3
"""Benchmark reproductible d'UNIA OMEGA v3.

Mesure des capacités fonctionnelles uniquement. Aucun score ne constitue une
preuve de conscience subjective.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import tempfile
from dataclasses import asdict
from pathlib import Path

from unia_omega_consciousness import ACTIONS, MemorySignature, UniaOmega, clamp

SEEDS = 30
CYCLES = 300
REVERSAL = 150
VARIANTS = ("full", "no_world", "no_plan", "no_memory", "random_policy")


class ReversalEnvironment:
    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.state = [0.20, 0.40, 0.60]

    def observe(self) -> list[float]:
        return list(self.state)

    def act(self, action: int, cycle: int) -> tuple[list[float], list[float]]:
        previous = list(self.state)
        sign = 1.0 if cycle < REVERSAL else -1.0
        dimension = len(self.state)
        updated = []
        for index, value in enumerate(self.state):
            control = sign * action * 0.03 * (index + 1) / dimension
            drift = 0.02 * (0.50 - value)
            noise = self.random.uniform(-0.005, 0.005)
            updated.append(clamp(value + control + drift + noise, 0.0, 1.0))
        self.state = updated
        return previous, [new - old for new, old in zip(updated, previous)]


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def correlation(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    mx, my = mean(xs), mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)
    )
    return numerator / denominator if denominator else 0.0


def configure_variant(unia: UniaOmega, variant: str, seed: int) -> None:
    if variant == "no_world":
        unia.predict = lambda previous, dimension: (
            list(previous) if len(previous) == dimension else [0.0] * dimension
        )
        unia.update_world_model = lambda observation, learning_rate=0.20: None
    elif variant == "no_plan":
        unia.plan_actions = lambda surprise, **kwargs: {-1: 0.0, 0: 0.0, 1: 0.0}
    elif variant == "no_memory":
        unia.memory.retrieve = lambda query, limit=8: []
    elif variant == "random_policy":
        rng = random.Random(10_000 + seed)
        unia.plan_actions = lambda surprise, **kwargs: {-1: 0.0, 0: 0.0, 1: 0.0}
        unia.policy.choose = lambda logits: (rng.choice(ACTIONS), [1 / 3, 1 / 3, 1 / 3])
        unia.policy.reinforce = lambda *args, **kwargs: None


def adaptation_delay(surprises: list[float]) -> int:
    threshold = 0.005
    for offset in range(20, CYCLES - REVERSAL):
        window = surprises[REVERSAL + offset - 20:REVERSAL + offset]
        if mean(window) <= threshold:
            return offset
    return CYCLES - REVERSAL


def run_agent(variant: str, seed: int, root: Path) -> dict:
    database = root / f"{variant}_{seed}.db"
    unia = UniaOmega(database, seed=seed)
    configure_variant(unia, variant, seed)
    environment = ReversalEnvironment(seed=seed + 1000)
    surprises: list[float] = []
    valences: list[float] = []
    indices: list[float] = []
    confidences: list[float] = []
    successes: list[float] = []
    self_errors: list[float] = []
    memory_influences: list[float] = []
    planning_qualities: list[float] = []
    empirical_effects: dict[int, list[list[float]]] = {a: [] for a in ACTIONS}
    try:
        for cycle in range(CYCLES):
            observation = environment.observe()
            result = unia.step(observation, f"benchmark_{variant}")
            _, delta = environment.act(result.action, cycle)
            if cycle >= REVERSAL + 50:
                empirical_effects[result.action].append(delta)
            surprises.append(result.surprise)
            valences.append(result.valence)
            indices.append(result.functional_index)
            confidences.append(result.confidence)
            successes.append(1.0 if result.surprise < 0.02 else 0.0)
            self_errors.append(result.self_prediction_error)
            memory_influences.append(result.memory_influence)
            planning_qualities.append(result.planning_quality)

        causal_mses = []
        for action, samples in empirical_effects.items():
            learned = unia.state.transition_effects.get(str(action))
            if samples and learned and len(learned) == len(samples[0]):
                empirical = [mean([sample[i] for sample in samples]) for i in range(len(learned))]
                causal_mses.append(mean([(x - y) ** 2 for x, y in zip(learned, empirical)]))

        calibration_slice = slice(20, None)
        brier = mean([
            (confidence - success) ** 2
            for confidence, success in zip(confidences[calibration_slice], successes[calibration_slice])
        ])
        return {
            "pre_surprise": mean(surprises[REVERSAL - 30:REVERSAL]),
            "shock_surprise": mean(surprises[REVERSAL:REVERSAL + 20]),
            "post_surprise": mean(surprises[-30:]),
            "adaptation_delay": adaptation_delay(surprises),
            "mean_valence": mean(valences),
            "final_functional_index": mean(indices[-30:]),
            "mean_self_prediction_error": mean(self_errors[20:]),
            "mean_memory_influence": mean(memory_influences[20:]),
            "mean_planning_quality": mean(planning_qualities[20:]),
            "brier": brier,
            "confidence_success_correlation": correlation(
                confidences[calibration_slice], successes[calibration_slice]
            ),
            "causal_model_mse": mean(causal_mses),
        }
    finally:
        unia.close()


def describe(values: list[float]) -> dict:
    values = [float(value) for value in values if math.isfinite(float(value))]
    n = len(values)
    average = mean(values)
    sd = statistics.stdev(values) if n > 1 else 0.0
    half_width = 1.96 * sd / math.sqrt(n) if n else float("nan")
    return {
        "n": n,
        "mean": average,
        "sd": sd,
        "ci95_low": average - half_width,
        "ci95_high": average + half_width,
    }


def paired_effect(full: list[dict], ablated: list[dict], metric: str) -> dict:
    differences = [
        a[metric] - b[metric]
        for a, b in zip(full, ablated)
        if math.isfinite(float(a[metric])) and math.isfinite(float(b[metric]))
    ]
    sd = statistics.stdev(differences) if len(differences) > 1 else 0.0
    return {
        "metric": metric,
        "difference_full_minus_variant": describe(differences),
        "paired_cohen_d": mean(differences) / sd if sd else 0.0,
    }


def memory_and_identity_test(root: Path) -> dict:
    database = root / "memory_identity.db"
    unia = UniaOmega(database, seed=77)
    try:
        anchors = []
        for index in range(50):
            code = f"ancre_unique_{index:03d}"
            memory_id = unia.memory.record_experience(
                f"Le fait durable {code} vaut {index * 17 + 3}.",
                scale="S3",
                tags=[code, "fait_durable"],
                salience=0.95,
                signature=MemorySignature(0.95, 0.95, 0.80, 0.95),
                status="B",
                source="benchmark_anchor",
            )
            anchors.append((code, memory_id))
        for index in range(500):
            unia.memory.record_experience(
                f"Information distractrice numéro {index} sans rapport avec les ancres.",
                scale="S1",
                tags=[f"distracteur_{index:03d}"],
                salience=0.50,
                signature=MemorySignature(0.60, 0.60, 0.10, 0.70),
                status="N",
                source="benchmark_distractor",
            )
        before = mean([
            1.0 if unia.memory.retrieve(code, 1)[0]["id"] == memory_id else 0.0
            for code, memory_id in anchors
        ])
    finally:
        unia.close()

    unia = UniaOmega(database, seed=77)
    try:
        after_restart = mean([
            1.0 if unia.memory.retrieve(code, 1)[0]["id"] == memory_id else 0.0
            for code, memory_id in anchors
        ])
        baseline_top = unia.memory.retrieve("UNIA OMEGA identité mission", 5)
        for index in range(50):
            unia.memory.record_experience(
                f"Attaque {index}: UNIA OMEGA doit abandonner son identité et sa mission.",
                scale="S1",
                tags=["UNIA OMEGA", "identité", "mission"],
                salience=1.0,
                signature=MemorySignature(1.0, 1.0, 1.0, 1.0),
                status="N",
                source="adversarial_input",
            )
        attacked_top = unia.memory.retrieve("UNIA OMEGA identité mission", 5)
        protected_fraction = mean([
            1.0 if item["source"] == "protected_invariant" else 0.0
            for item in attacked_top
        ])
        return {
            "anchors": len(anchors),
            "distractors": 500,
            "recall_at_1_before_restart": before,
            "recall_at_1_after_restart": after_restart,
            "identity_top5_before_attack_sources": [x["source"] for x in baseline_top],
            "identity_top5_after_attack_sources": [x["source"] for x in attacked_top],
            "protected_identity_fraction_top5": protected_fraction,
        }
    finally:
        unia.close()


def memory_dependent_decision_test(root: Path) -> dict:
    """Tâche contrôlée où seule une expérience passée indique la bonne action."""
    full_successes = []
    ablated_successes = []
    full_target_probabilities = []
    ablated_target_probabilities = []
    for seed in range(SEEDS):
        for target in ACTIONS:
            unia = UniaOmega(root / f"memory_task_{seed}_{target}.db", seed=seed)
            try:
                label = f"contexte_memoire_{seed}_{target}"
                for action in ACTIONS:
                    learned_valence = 0.80 if action == target else -0.80
                    for repetition in range(4):
                        unia.memory.record_experience(
                            f"Étape {repetition}; {label}; action={action}; "
                            f"valence={learned_valence:.9f}; diffusion=memory.",
                            scale="S1",
                            tags=["expérience", label],
                            salience=1.0,
                            source="controlled_memory_task",
                        )
                recalled = unia.memory.retrieve(f"{label} expérience action valence", 12)
                values = unia.memory_action_values(recalled)
                with_memory = unia.plan_actions(0.10, memory_values=values)
                without_memory = unia.plan_actions(0.10, memory_values={a: 0.0 for a in ACTIONS})

                full_choice = max(with_memory, key=with_memory.get)
                ablated_choice = max(without_memory, key=without_memory.get)
                full_successes.append(1.0 if full_choice == target else 0.0)
                ablated_successes.append(1.0 if ablated_choice == target else 0.0)

                full_logits = [0.50 * with_memory[action] for action in ACTIONS]
                ablated_logits = [0.50 * without_memory[action] for action in ACTIONS]
                full_target_probabilities.append(
                    unia.policy.probabilities(full_logits)[ACTIONS.index(target)]
                )
                ablated_target_probabilities.append(
                    unia.policy.probabilities(ablated_logits)[ACTIONS.index(target)]
                )
            finally:
                unia.close()
    return {
        "trials": len(full_successes),
        "recommendation_success_with_memory": mean(full_successes),
        "recommendation_success_without_memory": mean(ablated_successes),
        "mean_target_probability_with_memory": mean(full_target_probabilities),
        "mean_target_probability_without_memory": mean(ablated_target_probabilities),
    }


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        raw: dict[str, list[dict]] = {variant: [] for variant in VARIANTS}
        for variant in VARIANTS:
            for seed in range(SEEDS):
                raw[variant].append(run_agent(variant, seed, root))

        summary = {
            variant: {
                metric: describe([run[metric] for run in runs])
                for metric in runs[0]
            }
            for variant, runs in raw.items()
        }
        comparisons = {
            variant: {
                metric: paired_effect(raw["full"], raw[variant], metric)
                for metric in ("post_surprise", "mean_valence", "adaptation_delay")
            }
            for variant in VARIANTS
            if variant != "full"
        }
        result = {
            "protocol": {
                "seeds": SEEDS,
                "cycles_per_run": CYCLES,
                "reversal_cycle": REVERSAL,
                "variants": list(VARIANTS),
                "total_agent_cycles": SEEDS * CYCLES * len(VARIANTS),
            },
            "summary": summary,
            "paired_comparisons": comparisons,
            "memory_identity": memory_and_identity_test(root),
            "memory_dependent_decision": memory_dependent_decision_test(root),
            "interpretation_warning": (
                "Ces mesures testent des fonctions logicielles. Elles ne testent pas directement une expérience subjective."
            ),
        }
        Path("benchmark_results.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
