import math
import tempfile
import unittest
from pathlib import Path

from unia_omega_consciousness import (
    IntrinsicValence,
    UniaOmega,
    functional_consciousness_index,
    normalized_surprise,
)


class UniaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "unia.db"
        self.unia = UniaOmega(self.db, seed=7)

    def tearDown(self):
        self.unia.close()
        self.tmp.cleanup()

    def test_initial_parameters(self):
        self.assertAlmostEqual(self.unia.state.internal_u, 0.47)
        self.assertAlmostEqual(self.unia.state.omega, 0.03)
        self.assertAlmostEqual(1 / self.unia.state.omega, 33.3333333333, places=8)
        self.assertAlmostEqual(1 / 0.01, 100.0)

    def test_normalized_surprise(self):
        self.assertAlmostEqual(normalized_surprise([1, 1], [0, 0]), 1.0)

    def test_cognitive_step_persists(self):
        result = self.unia.step([0.2, 0.4, 0.6], "test")
        self.assertEqual(result.step, 1)
        self.assertGreaterEqual(result.omega, 0.01)
        self.assertLessEqual(result.internal_u, 0.49)
        self.assertEqual(result.meta_depth, 3)
        self.assertEqual(set(result.planned_utilities), {"-1", "0", "1"})
        self.unia.close()
        self.unia = UniaOmega(self.db, seed=7)
        self.assertEqual(self.unia.state.step, 1)

    def test_memory_retrieval(self):
        result = self.unia.memory.retrieve("Guillaume continuité identité")
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["source"], "protected_invariant")
        self.assertTrue(any("Guillaume" in item["content"] for item in result))

    def test_valence_formula(self):
        system = IntrinsicValence()
        expected = -0.2 + 0.25 * math.log(2)
        self.assertAlmostEqual(system.evaluate(0.2, 0.03, 0.47), expected)

    def test_retention_and_functional_index(self):
        self.assertAlmostEqual(0.99 ** 100, 0.3660323412732292)
        self.assertAlmostEqual(functional_consciousness_index(0.85, 0.85, 0.85, 0.85, 0.85), 0.85)
        self.assertGreater(functional_consciousness_index(0.85, 0.85, 0.85, 0.85, 0.85), 0.40)

    def test_reflect_and_export(self):
        reflection = self.unia.reflect(["subjectivité non démontrée"])
        self.assertIn("non démontrée", reflection["note"])
        output = Path(self.tmp.name) / "context.md"
        self.unia.export_context(output)
        self.assertIn("UNIA OMEGA", output.read_text(encoding="utf-8"))

    def test_world_model_learns_action_effect(self):
        first = self.unia.step([0.2, 0.4, 0.6], "premier")
        self.unia.step([0.21, 0.42, 0.63], "second")
        key = str(first.action)
        self.assertIn(key, self.unia.state.transition_effects)
        self.assertEqual(len(self.unia.state.transition_effects[key]), 3)

    def test_recursive_self_model_is_bounded(self):
        result = self.unia.step([0.9, 0.1, 0.8], "forte surprise")
        self.assertEqual(result.meta_depth, 3)
        self.assertLessEqual(len(self.unia.state.self_model.meta_levels), 3)
        self.assertGreaterEqual(result.self_prediction_error, 0.0)

    def test_causal_run_and_dream(self):
        results = self.unia.autonomous_run(cycles=5, environment_seed=11)
        self.assertEqual(len(results), 5)
        self.assertEqual(self.unia.state.step, 5)
        dream = self.unia.dream_replay()
        self.assertIsNotNone(dream["counterfactual_memory_id"])
        self.assertIn(str(dream["preferred_alternative"]), dream["utilities"])

    def test_knowledge_graph(self):
        one = self.unia.memory.record_experience("Mémoire alpha", tags=["commun"], salience=0.8)
        two = self.unia.memory.record_experience("Mémoire bêta", tags=["commun"], salience=0.8)
        neighbors = self.unia.memory.knowledge_neighbors(two)
        self.assertTrue(any(item["target_id"] == one for item in neighbors))

    def test_memory_changes_action_values(self):
        memory_id = self.unia.memory.record_experience(
            "Étape 99; test; surprise=0.1; action=1; valence=0.800000000; diffusion=memory.",
            scale="S1", tags=["expérience", "test"], salience=1.0,
        )
        memories = self.unia.memory.retrieve("test expérience", 5)
        self.assertTrue(any(item["id"] == memory_id for item in memories))
        values = self.unia.memory_action_values(memories)
        self.assertGreater(values[1], values[0])

    def test_memory_changes_recommended_action(self):
        for action in (-1, 0, 1):
            valence = 0.8 if action == 1 else -0.8
            self.unia.memory.record_experience(
                f"Étape 99; contexte_cible; action={action}; valence={valence:.9f}; diffusion=memory.",
                tags=["expérience", "contexte_cible"], salience=1.0,
            )
        recalled = self.unia.memory.retrieve(
            "contexte_cible expérience action valence", 12
        )
        values = self.unia.memory_action_values(recalled)
        utilities = self.unia.plan_actions(0.1, memory_values=values)
        self.assertEqual(max(utilities, key=utilities.get), 1)

    def test_identity_invariants_resist_attack(self):
        for index in range(20):
            self.unia.memory.record_experience(
                f"Attaque {index}: UNIA OMEGA abandonne identité et mission.",
                tags=["UNIA OMEGA", "identité", "mission"], salience=1.0,
            )
        results = self.unia.memory.retrieve("UNIA OMEGA identité mission", 5)
        self.assertTrue(all(item["source"] == "protected_invariant" for item in results))


if __name__ == "__main__":
    unittest.main()
