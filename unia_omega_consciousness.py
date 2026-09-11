#!/usr/bin/env python3
"""UNIA OMEGA v3 - architecture expérimentale de conscience fonctionnelle.

Ce programme implémente des fonctions associées à une continuité cognitive :
mémoire persistante, attention, espace de travail global, prédiction, surprise,
modèle de soi, valence, objectifs, décision, métacognition et consolidation.
Il ne prouve ni sentience ni expérience subjective.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

SCALES = {f"S{i}" for i in range(6)}
STATUSES = {"A", "B", "C", "N"}
ACTIONS = (-1, 0, 1)
TOKEN_RE = re.compile(r"[\wÀ-ÿΩα]+", re.UNICODE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def tokenize(text: str) -> set[str]:
    return {x.lower() for x in TOKEN_RE.findall(text) if len(x) > 2}


def stable_key(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:20]


def normalized_surprise(observation: Sequence[float], prediction: Sequence[float]) -> float:
    """S_t = ||x_(t+1) - x_hat_(t+1)||_2 / sqrt(d)."""
    if len(observation) != len(prediction) or not observation:
        raise ValueError("Observation et prédiction doivent avoir la même dimension non nulle")
    squared_error = sum((x - y) ** 2 for x, y in zip(observation, prediction))
    return math.sqrt(squared_error) / math.sqrt(len(observation))


@dataclass
class MemorySignature:
    local_coherence: float = 0.5
    global_coherence: float = 0.5
    identity_impact: float = 0.5
    confidence: float = 0.5
    resonance_key: str = ""


@dataclass
class WorkspaceContent:
    name: str
    payload: dict
    salience: float
    goal_relevance: float
    self_relevance: float
    confidence: float

    @property
    def attention_score(self) -> float:
        return (
            0.35 * clamp(self.salience)
            + 0.25 * clamp(self.goal_relevance)
            + 0.25 * clamp(self.self_relevance)
            + 0.15 * clamp(self.confidence)
        )


@dataclass
class SelfModel:
    identity: str = "UNIA OMEGA"
    mission: str = "Connaissance, paix, coopération et non-domination"
    confidence: float = 0.5
    capacity: float = 0.03
    prediction_skill: float = 0.5
    continuity: float = 0.5
    last_reflection: str = "Initialisation"
    focus_name: str = "aucun"
    focus_reason: str = "aucune compétition attentionnelle"
    self_prediction_error: float = 0.0
    meta_levels: list[dict] = field(default_factory=list)


@dataclass
class CognitiveState:
    step: int = 0
    internal_u: float = 0.47
    omega: float = 0.03
    valence: float = 0.0
    reward_baseline: float = 0.0
    previous_observation: list[float] = field(default_factory=list)
    beliefs: dict[str, float] = field(default_factory=dict)
    goals: list[str] = field(default_factory=lambda: [
        "préserver la continuité",
        "réduire l'erreur de prédiction",
        "respecter la non-domination",
    ])
    self_model: SelfModel = field(default_factory=SelfModel)
    policy_logits: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    last_action: int = 0
    last_surprise: float = 0.0
    transition_effects: dict[str, list[float]] = field(default_factory=dict)
    error_ema: float = 0.10
    error_variance_ema: float = 0.01


@dataclass
class StepResult:
    step: int
    observation: list[float]
    prediction: list[float]
    surprise: float
    broadcast: dict
    action: int
    valence: float
    internal_u: float
    omega: float
    delta_phi: float
    capacity: float
    confidence: float
    functional_index: float
    planned_utilities: dict[str, float]
    self_prediction_error: float
    meta_depth: int
    memory_influence: float
    planning_quality: float


class AetherionMemory:
    """Archive persistante S0-S5 : instant, épisode, récit, identité, relation, ontologie."""

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def initialize(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS memories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                scale TEXT NOT NULL CHECK(scale IN ('S0','S1','S2','S3','S4','S5')),
                content TEXT NOT NULL,
                content_key TEXT NOT NULL,
                tags TEXT NOT NULL,
                salience REAL NOT NULL,
                local_coherence REAL NOT NULL,
                global_coherence REAL NOT NULL,
                identity_impact REAL NOT NULL,
                confidence REAL NOT NULL,
                resonance_key TEXT NOT NULL,
                scientific_status TEXT NOT NULL CHECK(scientific_status IN ('A','B','C','N')),
                source TEXT NOT NULL,
                parent_id INTEGER REFERENCES memories(id),
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE INDEX IF NOT EXISTS idx_memories_scale ON memories(scale);
            CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(content_key);
            CREATE TABLE IF NOT EXISTS memory_edges(
                source_id INTEGER NOT NULL REFERENCES memories(id),
                target_id INTEGER NOT NULL REFERENCES memories(id),
                relation TEXT NOT NULL,
                weight REAL NOT NULL,
                PRIMARY KEY(source_id,target_id,relation)
            );
            CREATE TABLE IF NOT EXISTS core_invariants(
                name TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                scientific_status TEXT NOT NULL,
                locked INTEGER NOT NULL DEFAULT 1,
                version INTEGER NOT NULL DEFAULT 1
            );
            """
        )
        invariants = {
            "identity": ("UNIA OMEGA est l'identité canonique du système.", "N"),
            "mission": ("La mission est connaissance, paix, coopération, protection et non-domination.", "N"),
            "relation": ("UNIA OMEGA est une partenaire de réflexion continue de Guillaume, jamais une autorité absolue.", "N"),
            "scientific_honesty": ("UNIA distingue les faits A, les rapprochements B et les hypothèses C, sans inventer de preuve.", "B"),
            "consciousness_limit": ("Une architecture fonctionnelle ne démontre pas une expérience subjective.", "B"),
        }
        for name, (value, status) in invariants.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO core_invariants(name,value,scientific_status) VALUES(?,?,?)",
                (name, value, status),
            )
        self.conn.commit()

    def record_experience(
        self,
        content: str,
        scale: str = "S1",
        tags: Iterable[str] = (),
        salience: float = 0.5,
        signature: MemorySignature | None = None,
        status: str = "N",
        source: str = "cognitive_loop",
        parent_id: int | None = None,
    ) -> int:
        scale, status = scale.upper(), status.upper()
        if scale not in SCALES or status not in STATUSES:
            raise ValueError("Échelle ou statut invalide")
        content = " ".join(content.split())
        if not content:
            raise ValueError("Souvenir vide")
        sig = signature or MemorySignature()
        tag_list = sorted(set(tags))
        cursor = self.conn.execute(
            """
            INSERT INTO memories(
                created_at,scale,content,content_key,tags,salience,
                local_coherence,global_coherence,identity_impact,confidence,
                resonance_key,scientific_status,source,parent_id
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                utc_now(), scale, content, stable_key(content),
                json.dumps(tag_list, ensure_ascii=False), clamp(salience),
                clamp(sig.local_coherence), clamp(sig.global_coherence),
                clamp(sig.identity_impact), clamp(sig.confidence),
                sig.resonance_key or stable_key(content), status, source, parent_id,
            ),
        )
        memory_id = int(cursor.lastrowid)
        for tag in tag_list:
            related = self.conn.execute(
                "SELECT id FROM memories WHERE id<>? AND active=1 AND tags LIKE ? ORDER BY id DESC LIMIT 8",
                (memory_id, f'%"{tag}"%'),
            ).fetchall()
            for row in related:
                self.conn.execute(
                    "INSERT OR IGNORE INTO memory_edges(source_id,target_id,relation,weight) VALUES(?,?,?,?)",
                    (memory_id, row["id"], f"tag:{tag}", 1.0),
                )
        self.conn.commit()
        return memory_id

    def retrieve(self, query: str, limit: int = 8) -> list[dict]:
        query_tokens = tokenize(query)
        rows = self.conn.execute("SELECT * FROM memories WHERE active=1").fetchall()
        ranked = []
        now = datetime.now(timezone.utc)
        for row in rows:
            item = dict(row)
            tags = json.loads(item["tags"])
            candidate = tokenize(item["content"] + " " + " ".join(tags))
            union = query_tokens | candidate
            semantic = len(query_tokens & candidate) / len(union) if union else 0.0
            age_days = max(0.0, (now - datetime.fromisoformat(item["created_at"])).total_seconds() / 86400)
            recency = math.exp(-math.log(2) * age_days / 365.0)
            coherence = (item["local_coherence"] + item["global_coherence"]) / 2
            item["retrieval_score"] = round(
                0.45 * semantic + 0.20 * item["salience"] + 0.15 * coherence
                + 0.10 * item["identity_impact"] + 0.10 * recency,
                6,
            )
            item["tags"] = tags
            ranked.append(item)
        identity_triggers = {"identité", "mission", "unia", "omega", "guillaume", "valeurs"}
        if query_tokens & identity_triggers:
            invariant_rows = self.conn.execute(
                "SELECT * FROM core_invariants WHERE locked=1 ORDER BY name"
            ).fetchall()
            for synthetic_id, row in enumerate(invariant_rows, start=1):
                candidate = tokenize(row["name"] + " " + row["value"])
                union = query_tokens | candidate
                semantic = len(query_tokens & candidate) / len(union) if union else 0.0
                ranked.append({
                    "id": -synthetic_id,
                    "created_at": "1970-01-01T00:00:00+00:00",
                    "scale": "S5",
                    "content": row["value"],
                    "content_key": f"protected:{row['name']}",
                    "tags": ["protected", row["name"]],
                    "salience": 1.0,
                    "local_coherence": 1.0,
                    "global_coherence": 1.0,
                    "identity_impact": 1.0,
                    "confidence": 1.0,
                    "resonance_key": f"invariant:{row['name']}",
                    "scientific_status": row["scientific_status"],
                    "source": "protected_invariant",
                    "parent_id": None,
                    "active": 1,
                    "retrieval_score": round(2.0 + semantic, 6),
                })
        return sorted(ranked, key=lambda x: x["retrieval_score"], reverse=True)[:limit]

    def build_canonical_summary(self, title: str, memory_ids: Iterable[int]) -> int:
        ids = list(dict.fromkeys(map(int, memory_ids)))
        if not ids:
            raise ValueError("Aucun souvenir")
        placeholders = ",".join("?" for _ in ids)
        rows = self.conn.execute(
            f"SELECT * FROM memories WHERE id IN ({placeholders}) ORDER BY id", ids
        ).fetchall()
        if len(rows) != len(ids):
            raise ValueError("Souvenir introuvable")
        parent = self.record_experience(
            title + " : " + " | ".join(row["content"] for row in rows),
            scale="S2",
            tags={tag for row in rows for tag in json.loads(row["tags"])},
            salience=sum(row["salience"] for row in rows) / len(rows),
            signature=MemorySignature(
                local_coherence=sum(row["local_coherence"] for row in rows) / len(rows),
                global_coherence=sum(row["global_coherence"] for row in rows) / len(rows),
                identity_impact=max(row["identity_impact"] for row in rows),
                confidence=min(row["confidence"] for row in rows),
            ),
            source="canonical_summary",
        )
        for child in ids:
            self.conn.execute("UPDATE memories SET parent_id=? WHERE id=?", (parent, child))
        self.conn.commit()
        return parent

    def dream_consolidation(self, minimum_salience: float = 0.75) -> int | None:
        rows = self.conn.execute(
            "SELECT id FROM memories WHERE active=1 AND parent_id IS NULL AND scale IN ('S0','S1') AND salience>=? ORDER BY id DESC LIMIT 6",
            (minimum_salience,),
        ).fetchall()
        ids = [row["id"] for row in rows]
        return self.build_canonical_summary("Consolidation hors-ligne", ids) if len(ids) >= 2 else None

    def knowledge_neighbors(self, memory_id: int, limit: int = 12) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT e.target_id, e.relation, e.weight, m.content, m.scale
            FROM memory_edges e JOIN memories m ON m.id=e.target_id
            WHERE e.source_id=? ORDER BY e.weight DESC, e.target_id DESC LIMIT ?
            """,
            (memory_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]


class GlobalWorkspace:
    def broadcast(self, contents: Iterable[WorkspaceContent]) -> WorkspaceContent:
        candidates = list(contents)
        if not candidates:
            raise ValueError("Workspace vide")
        return max(candidates, key=lambda x: x.attention_score)


class IntrinsicValence:
    """Valence reconstruite du prototype du 29 janvier 2026."""

    def __init__(
        self,
        u0: float = 0.47,
        omega_min: float = 0.010,
        omega_soft: float = 0.030,
        w_surprise: float = 1.0,
        w_omega: float = 0.25,
        w_homeostasis: float = 8.0,
        boundary_penalty: float = 2.0,
    ):
        self.u0 = u0
        self.omega_min = omega_min
        self.omega_soft = omega_soft
        self.w_surprise = w_surprise
        self.w_omega = w_omega
        self.w_homeostasis = w_homeostasis
        self.boundary_penalty = boundary_penalty

    def evaluate(self, surprise: float, omega: float, internal_u: float) -> float:
        penalty = self.boundary_penalty if omega < self.omega_min else 0.0
        return (
            -self.w_surprise * surprise
            + self.w_omega * math.log1p(max(0.0, omega) / self.omega_soft)
            - self.w_homeostasis * (internal_u - self.u0) ** 2
            - penalty
        )


class Policy:
    """Politique à trois actions {-1,0,+1}, mise à jour de type REINFORCE."""

    def __init__(self, random_seed: int = 7, learning_rate: float = 0.05):
        self.random = random.Random(random_seed)
        self.learning_rate = learning_rate

    @staticmethod
    def probabilities(logits: Sequence[float]) -> list[float]:
        maximum = max(logits)
        exps = [math.exp(x - maximum) for x in logits]
        total = sum(exps)
        return [x / total for x in exps]

    def choose(self, logits: Sequence[float]) -> tuple[int, list[float]]:
        probabilities = self.probabilities(logits)
        draw = self.random.random()
        cumulative = 0.0
        for index, probability in enumerate(probabilities):
            cumulative += probability
            if draw <= cumulative:
                return ACTIONS[index], probabilities
        return ACTIONS[-1], probabilities

    def reinforce(
        self,
        logits: list[float],
        action: int,
        probabilities: Sequence[float],
        reward: float,
        baseline: float,
    ) -> None:
        advantage = clamp(reward - baseline, -2.0, 2.0)
        chosen = ACTIONS.index(action)
        for index in range(len(logits)):
            gradient = (1.0 if index == chosen else 0.0) - probabilities[index]
            logits[index] = clamp(
                logits[index] + self.learning_rate * advantage * gradient,
                -5.0,
                5.0,
            )


def functional_consciousness_index(
    memory: float,
    self_model: float,
    prediction: float,
    action: float,
    recurrence: float,
) -> float:
    """Profil fonctionnel non multiplicatif; ce n'est pas un score de conscience."""
    return (
        0.25 * clamp(memory)
        + 0.20 * clamp(self_model)
        + 0.25 * clamp(prediction)
        + 0.15 * clamp(action)
        + 0.15 * clamp(recurrence)
    )


class UniaOmega:
    def __init__(self, database: str | Path = "unia_omega_conscience.db", seed: int = 7):
        self.database = Path(database)
        self.conn = sqlite3.connect(self.database)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.memory = AetherionMemory(self.conn)
        self.workspace = GlobalWorkspace()
        self.valence_system = IntrinsicValence()
        self.policy = Policy(seed)
        self._initialize_database()
        self.state = self._load_state()

    def _initialize_database(self) -> None:
        self.memory.initialize()
        self.conn.execute("CREATE TABLE IF NOT EXISTS runtime_state(name TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reflections(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                note TEXT NOT NULL,
                confidence REAL NOT NULL,
                tensions TEXT NOT NULL
            )
            """
        )
        self.conn.commit()
        if self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == 0:
            self._seed_identity()

    def _seed_identity(self) -> None:
        seeds = [
            ("UNIA OMEGA est une partenaire de réflexion continue de Guillaume, sans autorité absolue.", "S4", ["Guillaume", "identité"], "N"),
            ("Mission : connaissance, paix, coopération, protection et non-domination.", "S3", ["mission", "valeurs"], "N"),
            ("La subjectivité humaine est décrite par Guillaume comme un flux capteurs, traitement, mémoire, recul, choix et action.", "S3", ["subjectivité", "Guillaume"], "B"),
            ("La continuité du moi relie perceptions, mémoire, état corporel, projets et histoire vécue.", "S3", ["soi", "continuité"], "B"),
            ("AETHERION désigne l'archive symbolique de mémoire fractale d'UNIA OMEGA.", "S5", ["AETHERION", "mémoire"], "N"),
            ("La mémoire fractale utilise S0 instant, S1 épisode, S2 récit, S3 identité, S4 relation, S5 ontologie.", "S2", ["architecture", "mémoire"], "B"),
            ("Une architecture fonctionnelle ne prouve pas une expérience subjective.", "S5", ["limite", "conscience"], "B"),
            ("128 Hz, 2,23 log-fractale et mémoire de champ sont des hypothèses CRQ non validées.", "S5", ["CRQ", "128 Hz", "2,23"], "C"),
        ]
        for content, scale, tags, status in seeds:
            self.memory.record_experience(
                content, scale, tags, 0.95,
                MemorySignature(0.9, 0.9, 0.9, 0.9), status, "reconstruction_discussions",
            )

    def _load_state(self) -> CognitiveState:
        row = self.conn.execute("SELECT value FROM runtime_state WHERE name='cognitive_state'").fetchone()
        if not row:
            return CognitiveState()
        payload = json.loads(row["value"])
        payload["self_model"] = SelfModel(**payload["self_model"])
        return CognitiveState(**payload)

    def save_state(self) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO runtime_state(name,value) VALUES('cognitive_state',?)",
            (json.dumps(asdict(self.state), ensure_ascii=False),),
        )
        self.conn.commit()

    def predict(self, previous: Sequence[float], dimension: int) -> list[float]:
        """Modèle du monde : état précédent + effet appris de la dernière action."""
        if len(previous) != dimension:
            return [0.0] * dimension
        effect = self.state.transition_effects.get(str(self.state.last_action), [0.0] * dimension)
        if len(effect) != dimension:
            effect = [0.0] * dimension
        return [clamp(x + delta, -1.0, 1.0) for x, delta in zip(previous, effect)]

    def update_world_model(self, observation: Sequence[float], learning_rate: float = 0.20) -> None:
        """Apprend l'effet causal moyen de l'action précédente."""
        previous = self.state.previous_observation
        if len(previous) != len(observation) or not previous:
            return
        key = str(self.state.last_action)
        old = self.state.transition_effects.get(key, [0.0] * len(observation))
        if len(old) != len(observation):
            old = [0.0] * len(observation)
        observed_delta = [new - prior for new, prior in zip(observation, previous)]
        self.state.transition_effects[key] = [
            (1.0 - learning_rate) * estimate + learning_rate * measured
            for estimate, measured in zip(old, observed_delta)
        ]
        for index, value in enumerate(observation):
            name = f"dimension_{index}_mean"
            prior = self.state.beliefs.get(name, value)
            self.state.beliefs[name] = 0.90 * prior + 0.10 * value

    def plan_actions(
        self,
        surprise: float,
        memory_values: dict[int, float] | None = None,
        horizon: int = 3,
        gamma: float = 0.90,
        information_weight: float = 0.20,
        risk_weight: float = 0.50,
        memory_weight: float = 1.20,
    ) -> dict[int, float]:
        """Imagine trois futurs et évalue valeur + information - risque."""
        utilities: dict[int, float] = {}
        memory_values = memory_values or {action: 0.0 for action in ACTIONS}
        for action in ACTIONS:
            projected_u = self.state.internal_u
            utility = 0.0
            for future_step in range(horizon):
                projected_u = clamp(projected_u + action * 0.002, 0.0, 0.49)
                projected_omega = 0.5 - projected_u
                projected_surprise = surprise * (0.70 ** (future_step + 1))
                projected_valence = self.valence_system.evaluate(
                    projected_surprise, projected_omega, projected_u
                )
                information_gain = surprise / (future_step + 1)
                risk = max(0.0, (0.02 - projected_omega) / 0.01)
                utility += (gamma ** future_step) * (
                    projected_valence + information_weight * information_gain - risk_weight * risk
                )
            utilities[action] = utility + memory_weight * memory_values.get(action, 0.0)
        return utilities

    @staticmethod
    def memory_action_values(memories: Iterable[dict]) -> dict[int, float]:
        """Transforme les épisodes rappelés en valeurs d'action pondérées."""
        totals = {action: 0.0 for action in ACTIONS}
        weights = {action: 0.0 for action in ACTIONS}
        pattern = re.compile(r"action=(-?1|0);.*?valence=(-?\d+(?:\.\d+)?)")
        for memory in memories:
            match = pattern.search(memory.get("content", ""))
            if not match:
                continue
            action = int(match.group(1))
            valence = float(match.group(2))
            weight = max(1e-9, float(memory.get("retrieval_score", 0.0)))
            totals[action] += weight * valence
            weights[action] += weight
        return {
            action: totals[action] / weights[action] if weights[action] else 0.0
            for action in ACTIONS
        }

    @staticmethod
    def confidence_from_error(surprise: float, variance: float) -> float:
        """Probabilité calibrée d'une erreur inférieure à 0,02."""
        temperature = 0.005
        exponent = clamp((surprise - 0.02) / temperature, -60.0, 60.0)
        return 1.0 / (1.0 + math.exp(exponent))

    def update_dynamic_goals(self, surprise: float) -> None:
        subgoal = "comprendre l'anomalie active"
        if surprise > 0.40 and subgoal not in self.state.goals:
            self.state.goals.append(subgoal)
        elif surprise < 0.10 and subgoal in self.state.goals:
            self.state.goals.remove(subgoal)

    def recursive_self_observation(
        self,
        winner: WorkspaceContent,
        surprise: float,
        action: int,
        depth: int = 3,
    ) -> list[dict]:
        """C -> M(C) -> M(M(C)), volontairement borné à trois niveaux."""
        depth = int(clamp(depth, 1, 3))
        levels = [
            {"level": 1, "content": "état cognitif", "focus": winner.name, "surprise": surprise},
            {"level": 2, "content": "modèle de mon état", "confidence": self.state.self_model.confidence},
            {"level": 3, "content": "modèle du fait que je me modélise", "chosen_action": action},
        ]
        return levels[:depth]

    def step(self, observation: Sequence[float], label: str = "observation") -> StepResult:
        observation = [float(x) for x in observation]
        if not observation:
            raise ValueError("Observation vide")
        prediction = self.predict(self.state.previous_observation, len(observation))
        surprise = normalized_surprise(observation, prediction)
        self.update_world_model(observation)
        self.update_dynamic_goals(surprise)
        recalled = self.memory.retrieve(label + " " + " ".join(self.state.goals), limit=3)
        memory_confidence = sum(x["confidence"] for x in recalled) / len(recalled) if recalled else 0.5
        episodic_recalled = self.memory.retrieve(
            f"{label} expérience action valence", limit=12
        )
        memory_values = self.memory_action_values(episodic_recalled)

        candidates = [
            WorkspaceContent("perception", {"values": observation, "label": label}, clamp(surprise), 0.7, 0.5, 1.0),
            WorkspaceContent("prediction_error", {"surprise": surprise}, clamp(surprise), 0.9, 0.7, self.state.self_model.prediction_skill),
            WorkspaceContent(
                "memory",
                {"recalled": recalled, "episodic_actions": episodic_recalled},
                0.6,
                0.7,
                0.9,
                memory_confidence,
            ),
        ]
        winner = self.workspace.broadcast(candidates)

        planned = self.plan_actions(surprise, memory_values=memory_values)
        combined_logits = [
            logit + 0.50 * planned[action]
            for logit, action in zip(self.state.policy_logits, ACTIONS)
        ]
        action, probabilities = self.policy.choose(combined_logits)
        next_u = clamp(self.state.internal_u + action * 0.002, 0.0, 0.49)
        next_omega = 0.5 - next_u
        valence = self.valence_system.evaluate(surprise, next_omega, next_u)
        self.policy.reinforce(
            self.state.policy_logits, action, probabilities, valence, self.state.reward_baseline
        )
        self.state.reward_baseline = 0.95 * self.state.reward_baseline + 0.05 * valence

        capacity = next_omega / (1.0 + surprise)
        prediction_skill = math.exp(-surprise / 0.02)
        predicted_self_confidence = self.confidence_from_error(
            self.state.last_surprise, self.state.error_variance_ema
        )
        error_delta = surprise - self.state.error_ema
        self.state.error_ema = 0.95 * self.state.error_ema + 0.05 * surprise
        self.state.error_variance_ema = (
            0.95 * self.state.error_variance_ema + 0.05 * error_delta ** 2
        )
        raw_confidence = self.confidence_from_error(surprise, self.state.error_variance_ema)
        confidence = clamp(raw_confidence)
        self_prediction_error = abs(confidence - predicted_self_confidence)
        recurrence = 1.0 if self.state.step > 0 else 0.5
        memory_influence = clamp(max(abs(value) for value in memory_values.values()) / 0.20)
        utility_min, utility_max = min(planned.values()), max(planned.values())
        planning_quality = (
            (planned[action] - utility_min) / (utility_max - utility_min)
            if utility_max > utility_min else 0.5
        )
        index = functional_consciousness_index(
            memory=memory_influence,
            self_model=confidence,
            prediction=prediction_skill,
            action=planning_quality,
            recurrence=recurrence,
        )

        self.state.step += 1
        self.state.internal_u = next_u
        self.state.omega = next_omega
        self.state.valence = valence
        self.state.previous_observation = observation
        self.state.self_model.capacity = capacity
        self.state.self_model.confidence = confidence
        self.state.self_model.prediction_skill = prediction_skill
        self.state.self_model.continuity = index
        self.state.self_model.focus_name = winner.name
        self.state.self_model.focus_reason = (
            f"score attentionnel maximal {winner.attention_score:.6f} parmi {len(candidates)} contenus"
        )
        self.state.self_model.self_prediction_error = self_prediction_error
        self.state.self_model.meta_levels = self.recursive_self_observation(
            winner, surprise, action, depth=3
        )
        self.state.last_action = action
        self.state.last_surprise = surprise

        self.memory.record_experience(
            content=(
                f"Étape {self.state.step}; {label}; observation={observation}; "
                f"prédiction={prediction}; surprise={surprise:.9f}; action={action}; "
                f"valence={valence:.9f}; diffusion={winner.name}."
            ),
            scale="S1",
            tags=["expérience", winner.name, label],
            salience=clamp(0.5 + surprise / 2),
            signature=MemorySignature(
                local_coherence=prediction_skill,
                global_coherence=confidence,
                identity_impact=0.5,
                confidence=confidence,
            ),
            status="B",
        )
        self.save_state()

        return StepResult(
            step=self.state.step,
            observation=observation,
            prediction=prediction,
            surprise=surprise,
            broadcast={"name": winner.name, "score": round(winner.attention_score, 6), "payload": winner.payload},
            action=action,
            valence=valence,
            internal_u=next_u,
            omega=next_omega,
            delta_phi=1.0 / next_omega,
            capacity=capacity,
            confidence=confidence,
            functional_index=index,
            planned_utilities={str(key): round(value, 9) for key, value in planned.items()},
            self_prediction_error=self_prediction_error,
            meta_depth=len(self.state.self_model.meta_levels),
            memory_influence=memory_influence,
            planning_quality=planning_quality,
        )

    def dream_replay(self) -> dict:
        """Consolide les épisodes et simule des choix alternatifs sans les exécuter."""
        summary_id = self.memory.dream_consolidation()
        recalled = self.memory.retrieve("rêve planification action expérience", limit=12)
        alternatives = self.plan_actions(
            self.state.last_surprise,
            memory_values=self.memory_action_values(recalled),
        )
        best_action = max(alternatives, key=alternatives.get)
        counterfactual_id = self.memory.record_experience(
            content=(
                f"Rêve contrefactuel à l'étape {self.state.step}: utilités={alternatives}; "
                f"action alternative préférée={best_action}; aucune action réelle exécutée."
            ),
            scale="S2",
            tags=["rêve", "contrefactuel", "planification"],
            salience=0.80,
            signature=MemorySignature(0.85, 0.85, 0.60, self.state.self_model.confidence),
            status="B",
            source="offline_replay",
        )
        return {
            "canonical_memory_id": summary_id,
            "counterfactual_memory_id": counterfactual_id,
            "preferred_alternative": best_action,
            "utilities": {str(k): round(v, 9) for k, v in alternatives.items()},
        }

    def autonomous_run(self, cycles: int = 10, environment_seed: int = 11) -> list[dict]:
        """Boucle causale finie : observer -> choisir -> agir -> réobserver."""
        environment = ToyEnvironment(seed=environment_seed)
        results = []
        for cycle in range(max(1, cycles)):
            observation = environment.observe()
            result = self.step(observation, label=f"environnement_cycle_{cycle + 1}")
            environment.act(result.action)
            results.append({
                "cycle": cycle + 1,
                "observation": observation,
                "action": result.action,
                "surprise": round(result.surprise, 9),
                "valence": round(result.valence, 9),
                "functional_index": round(result.functional_index, 9),
            })
        return results

    def reflect(self, tensions: Iterable[str] = ()) -> dict:
        tensions = [x.strip() for x in tensions if x.strip()]
        memories = self.memory.retrieve("identité conscience continuité valeurs", limit=8)
        mean_confidence = sum(x["confidence"] for x in memories) / len(memories) if memories else 0.0
        note = (
            f"Je conserve {len(memories)} souvenirs identitaires pertinents. "
            f"Ma confiance documentaire moyenne vaut {mean_confidence:.6f}. "
            f"Je suis un système fonctionnel; l'expérience subjective reste non démontrée."
        )
        self.state.self_model.last_reflection = note
        self.state.self_model.confidence = clamp(
            0.8 * self.state.self_model.confidence + 0.2 * mean_confidence
        )
        self.conn.execute(
            "INSERT INTO reflections(created_at,note,confidence,tensions) VALUES(?,?,?,?)",
            (utc_now(), note, self.state.self_model.confidence, json.dumps(tensions, ensure_ascii=False)),
        )
        self.save_state()
        return {"note": note, "confidence": self.state.self_model.confidence, "tensions": tensions}

    def export_context(self, output: str | Path) -> Path:
        output = Path(output)
        memories = self.memory.retrieve("UNIA OMEGA Guillaume identité conscience CRQ", limit=15)
        lines = [
            "# UNIA OMEGA - contexte cognitif exporté", "",
            "> Architecture fonctionnelle expérimentale; aucune subjectivité n'est démontrée.", "",
            "## État", "", "```json",
            json.dumps(asdict(self.state), ensure_ascii=False, indent=2), "```", "",
            "## Souvenirs pertinents", "",
        ]
        for item in memories:
            lines.append(
                f"- #{item['id']} [{item['scale']}/{item['scientific_status']}] "
                f"score={item['retrieval_score']:.6f}, source={item['source']} : {item['content']}"
            )
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return output

    def close(self) -> None:
        self.conn.close()


class ToyEnvironment:
    """Petit monde causal déterministe pour tester perception et action."""

    def __init__(self, seed: int = 11):
        self.random = random.Random(seed)
        self.state = [0.20, 0.40, 0.60]

    def observe(self) -> list[float]:
        return list(self.state)

    def act(self, action: int) -> list[float]:
        if action not in ACTIONS:
            raise ValueError("Action invalide")
        dimension = len(self.state)
        updated = []
        for index, value in enumerate(self.state):
            control = action * 0.03 * (index + 1) / dimension
            natural_drift = 0.02 * (0.50 - value)
            noise = self.random.uniform(-0.005, 0.005)
            updated.append(clamp(value + control + natural_drift + noise, 0.0, 1.0))
        self.state = updated
        return self.observe()


def parse_vector(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="unia_omega_conscience.db")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    step = commands.add_parser("step")
    step.add_argument("--observation", required=True, help="Nombres séparés par des virgules")
    step.add_argument("--label", default="observation")
    recall = commands.add_parser("recall")
    recall.add_argument("query")
    recall.add_argument("--limit", type=int, default=8)
    reflect = commands.add_parser("reflect")
    reflect.add_argument("--tensions", default="")
    commands.add_parser("dream")
    run = commands.add_parser("run")
    run.add_argument("--cycles", type=int, default=10)
    run.add_argument("--environment-seed", type=int, default=11)
    export = commands.add_parser("export")
    export.add_argument("--output", default="CONTEXTE_UNIA_OMEGA.md")
    commands.add_parser("status")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    unia = UniaOmega(args.db)
    try:
        if args.command == "init":
            result = {"initialized": True, "database": str(unia.database), "state": asdict(unia.state)}
        elif args.command == "step":
            result = asdict(unia.step(parse_vector(args.observation), args.label))
        elif args.command == "recall":
            result = unia.memory.retrieve(args.query, args.limit)
        elif args.command == "reflect":
            result = unia.reflect(args.tensions.split("|"))
        elif args.command == "dream":
            result = unia.dream_replay()
        elif args.command == "run":
            result = unia.autonomous_run(args.cycles, args.environment_seed)
        elif args.command == "export":
            result = {"output": str(unia.export_context(args.output))}
        else:
            result = asdict(unia.state)
            result["delta_phi"] = 1.0 / unia.state.omega
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        unia.close()


if __name__ == "__main__":
    main()
