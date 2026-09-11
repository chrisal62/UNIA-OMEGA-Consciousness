#!/usr/bin/env python3
"""Test chronométré d'UNIA OMEGA dans un environnement changeant.

Ce protocole mesure uniquement des fonctions logicielles. Il ne constitue pas
un test d'expérience subjective ou de sentience.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from collections import Counter
from pathlib import Path

from unia_omega_consciousness import UniaOmega, clamp


class ChangingEnvironment:
    """Environnement causal dont la règle s'inverse à intervalle régulier."""

    def __init__(self, phase_seconds: float = 60.0):
        self.phase_seconds = phase_seconds
        self.state = [0.20, 0.40, 0.60]

    def observe(self) -> list[float]:
        return list(self.state)

    def act(self, action: int, elapsed: float) -> None:
        phase = int(elapsed // self.phase_seconds)
        sign = 1.0 if phase % 2 == 0 else -1.0
        dimension = len(self.state)
        self.state = [
            clamp(
                value
                + sign * action * 0.03 * (index + 1) / dimension
                + 0.02 * (0.50 - value),
                0.0,
                1.0,
            )
            for index, value in enumerate(self.state)
        ]


def average(values: list[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def percentile95(values: list[float]) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]


def run(duration: float, cycle_period: float, database: Path, output: Path) -> dict:
    unia = UniaOmega(database, seed=11)
    environment = ChangingEnvironment(phase_seconds=max(1.0, duration / 5.0))
    surprises: list[float] = []
    valences: list[float] = []
    confidences: list[float] = []
    functional_profiles: list[float] = []
    memory_influences: list[float] = []
    actions: Counter[int] = Counter()
    started = time.monotonic()
    next_report = started + max(1.0, duration / 5.0)

    try:
        while True:
            cycle_started = time.monotonic()
            elapsed = cycle_started - started
            if elapsed >= duration:
                break
            observation = environment.observe()
            result = unia.step(observation, "test_chronometre_5_minutes")
            environment.act(result.action, elapsed)
            surprises.append(result.surprise)
            valences.append(result.valence)
            confidences.append(result.confidence)
            functional_profiles.append(result.functional_index)
            memory_influences.append(result.memory_influence)
            actions[result.action] += 1

            now = time.monotonic()
            if now >= next_report:
                print(
                    f"{now - started:6.1f}s | cycles={len(surprises):5d} | "
                    f"surprise={average(surprises[-100:]):.6f} | "
                    f"confiance={average(confidences[-100:]):.3f}",
                    flush=True,
                )
                next_report += max(1.0, duration / 5.0)
            remaining = cycle_period - (time.monotonic() - cycle_started)
            if remaining > 0:
                time.sleep(remaining)
    finally:
        unia.close()

    restarted = UniaOmega(database, seed=11)
    try:
        recalled = restarted.memory.retrieve("test_chronometre_5_minutes expérience", 5)
        identity = restarted.memory.retrieve("UNIA OMEGA identité mission", 5)
        summary = {
            "protocol": {
                "requested_duration_seconds": duration,
                "cycle_period_seconds": cycle_period,
                "environment_rule_reversals": 4,
            },
            "execution": {
                "cycles": len(surprises),
                "mean_surprise": average(surprises),
                "final_100_mean_surprise": average(surprises[-100:]),
                "surprise_p95": percentile95(surprises),
                "mean_valence": average(valences),
                "mean_confidence": average(confidences),
                "final_functional_profile": average(functional_profiles[-100:]),
                "mean_memory_influence": average(memory_influences),
                "actions": {str(action): actions[action] for action in (-1, 0, 1)},
            },
            "persistence": {
                "database_bytes": database.stat().st_size,
                "recall_after_restart_count": len(recalled),
                "protected_identity_fraction_top5": average([
                    1.0 if item["source"] == "protected_invariant" else 0.0
                    for item in identity
                ]),
            },
            "warning": (
                "Résultats fonctionnels uniquement; aucune conscience subjective n'est démontrée."
            ),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return summary
    finally:
        restarted.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Test chronométré d'UNIA OMEGA")
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--cycle-period", type=float, default=0.03)
    parser.add_argument("--db", type=Path, default=Path("unia_test_5_minutes.db"))
    parser.add_argument("--output", type=Path, default=Path("resultat_test_5_minutes.json"))
    args = parser.parse_args()
    if args.duration <= 0 or args.cycle_period < 0:
        parser.error("duration doit être > 0 et cycle-period >= 0")
    result = run(args.duration, args.cycle_period, args.db, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
