"""Provider adapters for the System One / decision-model protocol.

Every provider speaks the same wire format:
    request  = {"state": <str|obj>, "questions": {id: {type, ...}}}
    response = {"answers": {id: {"type": ..., "choice"|"score"|"noul": ...,
                                 "probabilities": {...}, "confidence": ...}}}

`noul` is the wire keyword for a yes/no judgement on some surfaces.
The Vercel AI Gateway calls the same thing `boolean` and rejects `noul`,
so normalise_helpers() translates at the adapter boundary.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

NUL_KEYWORDS = ("noul", "boolean")


# --------------------------------------------------------------------- helpers
def normalise_questions(questions: dict, wire_keyword: str = "noul") -> dict:
    """Translate our canonical question types into a provider's wire keywords."""
    out = {}
    for qid, q in questions.items():
        q = dict(q)
        if q.get("type") == "noul" and wire_keyword != "noul":
            q["type"] = wire_keyword
        out[qid] = q
    return out


def normalise_answers(answers: dict) -> dict:
    """Flatten provider answers into one comparable shape.

    Returns {qid: {"kind", "value", "probabilities", "confidence"}}.
    """
    out = {}
    for qid, a in answers.items():
        kind = a.get("type")
        if kind in ("noul", "boolean"):
            kind = "noul"
            value = a.get("noul", a.get("boolean"))
        elif kind == "choice":
            value = a.get("choice")
        elif kind == "score":
            value = a.get("score")
        else:
            value = a.get("value")
        out[qid] = {
            "kind": kind,
            "value": value,
            "probabilities": a.get("probabilities") or {},
            "confidence": a.get("confidence"),
        }
    return out


def _post_json(url: str, headers: dict, payload: dict, timeout: int = 60) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


@dataclass
class Provider:
    name: str
    price_per_mtok: float = 0.0
    wire_keyword: str = "noul"
    supports_images: bool = False
    notes: str = ""
    _last_usage: dict = field(default_factory=dict, repr=False)

    def decide(self, state: Any, questions: dict) -> dict:  # pragma: no cover
        raise NotImplementedError

    def estimate_cost(self, usage: dict) -> float:
        tok = (usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
        return tok * self.price_per_mtok / 1_000_000


# ------------------------------------------------------------------- TypeSafe
class JevProvider(Provider):
    """TypeSafe Jev — https://api.typesafe.ai/v1/systemone

    Env: TYPESAFE_API_KEY. Model: jev-latest | jev-1.14.0 | jev-1.13.0
    """
    URL = "https://api.typesafe.ai/v1/systemone"

    def __init__(self, model: str = "jev-latest", api_key: str | None = None,
                 price_per_mtok: float = 0.042, timeout: int = 60):
        super().__init__(name=f"jev:{model}", price_per_mtok=price_per_mtok)
        self.model = model
        self.api_key = api_key or os.environ.get("TYPESAFE_API_KEY", "")
        self.timeout = timeout

    def decide(self, state, questions):
        if not self.api_key:
            raise RuntimeError("TYPESAFE_API_KEY is not set")
        payload = {
            "model": self.model,
            "state": state,
            "questions": normalise_questions(questions, self.wire_keyword),
        }
        resp = _post_json(self.URL, {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }, payload, self.timeout)
        self._last_usage = resp.get("usage") or {}
        return normalise_answers(resp.get("answers") or {})


# ------------------------------------------------------------------ Cloudflare
class ClefProvider(Provider):
    """Cloudflare Clef / clef-flash on Workers AI.

    Env: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_AUTH_TOKEN
    Prices (VERIFIED, Cloudflare model pages): clef $0.24/Mtok, clef-flash $0.038/Mtok
    """
    PRICES = {"clef": 0.24, "clef-flash": 0.038}

    def __init__(self, model: str = "clef-flash", account_id: str | None = None,
                 token: str | None = None, timeout: int = 60):
        super().__init__(name=f"clef:{model}",
                         price_per_mtok=self.PRICES.get(model, 0.24),
                         supports_images=True)
        self.model = model
        self.account_id = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        self.token = token or os.environ.get("CLOUDFLARE_AUTH_TOKEN", "")
        self.timeout = timeout

    def url(self) -> str:
        return (f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}"
                f"/ai/run/@cf/cloudflare/{self.model}")

    def decide(self, state, questions, images: list | None = None):
        if not (self.account_id and self.token):
            raise RuntimeError("CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_AUTH_TOKEN not set")
        payload = {
            "model": self.model,
            "state": state,
            "questions": normalise_questions(questions, self.wire_keyword),
        }
        if images:
            payload["images"] = images
        resp = _post_json(self.url(), {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }, payload, self.timeout)
        if not resp.get("success", True):
            raise RuntimeError(f"Cloudflare error: {resp.get('errors')}")
        result = resp.get("result") or {}
        self._last_usage = result.get("usage") or {}
        return normalise_answers(result.get("answers") or {})


# ------------------------------------------- OpenAI-compatible (pplx-decider)
class OpenAICompatibleProvider(Provider):
    """Any OpenAI-compatible endpoint, e.g. pplx-decider-v1-27b via OpenRouter.

    Env: OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
    NOTE: decision models on these gateways may not accept the native
    noul/choice/score schema; you often have to force a JSON schema in the
    response_format and parse the JSON out of the message. That parsing step
    is exactly what this category removes - treat those numbers as
    "schema-adapter overhead", not as the model's raw quality.
    """
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, price_per_mtok: float = 0.02, timeout: int = 90):
        super().__init__(name=f"oai:{model or os.environ.get('OPENAI_MODEL', 'unknown')}",
                         price_per_mtok=price_per_mtok)
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model or os.environ.get("OPENAI_MODEL", "")
        self.timeout = timeout

    def decide(self, state, questions):
        if not (self.base_url and self.api_key and self.model):
            raise RuntimeError("OPENAI_BASE_URL / OPENAI_API_KEY / OPENAI_MODEL not set")
        prompt = {
            "state": state,
            "questions": normalise_questions(questions, self.wire_keyword),
            "instructions": "Answer every question. Return JSON: "
                            '{"answers": {qid: {type, value, probabilities, confidence}}}',
        }
        resp = _post_json(f"{self.base_url}/chat/completions", {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }, {
            "model": self.model,
            "messages": [{"role": "user", "content": json.dumps(prompt)}],
            "temperature": 0,
        }, self.timeout)
        self._last_usage = resp.get("usage") or {}
        content = resp["choices"][0]["message"]["content"]
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"non-JSON content from {self.name}: {content[:200]!r}")
        return normalise_answers(payload.get("answers") or {})


# ----------------------------------------------------------------------- mock
class MockProvider(Provider):
    """Deterministic offline simulator — for testing the HARNESS, not the models.

    It is deliberately NOT a model evaluation. It reproduces the *shape* of the
    published findings so the pipeline (metrics, swap matrix, format-friction
    report) can be exercised without API keys:

      * `noul` answers shift with the state's serialisation shape
        (prose / flat / nested) -- mimicking the reported 0.90 vs 0.09 swing
      * `choice` and `score` answers are stable across formats
      * `noul` carries no confidence, `choice`/`score` do
      * probabilities are drawn from a hash of the state so repeats are stable
    """

    FORMAT_SHIFT = {"prose": 0.0, "flat": -0.04, "nested": -0.81}

    def __init__(self, name: str = "mock", price_per_mtok: float = 0.042,
                 jitter: float = 0.0, seed: str = "decisionarena"):
        super().__init__(name=name, price_per_mtok=price_per_mtok)
        self.jitter = jitter
        self.seed = seed

    @staticmethod
    def _detect_format(state) -> str:
        if isinstance(state, dict):
            for v in state.values():
                if isinstance(v, (dict, list)):
                    return "nested"
            return "flat"
        text = str(state)
        if text.lstrip().startswith("{"):
            return "nested" if "[" in text or '"' in text else "flat"
        return "prose"

    def decide(self, state, questions):
        fmt = self._detect_format(state)
        shift = self.FORMAT_SHIFT.get(fmt, 0.0)
        answers = {}
        for qid, q in questions.items():
            h = hashlib.sha256(f"{self.seed}|{qid}|{json.dumps(state, sort_keys=True, default=str)}".encode())
            u = int(h.hexdigest()[:8], 16) / 0xFFFFFFFF  # 32-bit slice -> uniform [0,1)
            qtype = q.get("type")
            if qtype == "noul":
                p = 0.5 + 0.45 * (u - 0.5) * 2 + shift
                p = min(max(p, 0.0), 1.0)
                answers[qid] = {"type": "noul", "noul": round(p, 4)}
            elif qtype == "choice":
                opts = list(q.get("criteria", {}).keys())
                if not opts:
                    continue
                raw = [(hashlib.sha256(f"{h.hexdigest()}{o}".encode()).hexdigest(), o) for o in opts]
                raw.sort(reverse=True)
                weights = [max(0.05, 1.0 - i * 0.3) for i in range(len(raw))]
                total = sum(weights)
                probs = {o: round(w / total, 4) for (_, o), w in zip(raw, weights)}
                top = max(probs, key=lambda k: probs[k])
                answers[qid] = {"type": "choice", "choice": top, "probabilities": probs,
                                "confidence": round(min(0.99, probs[top] + 0.05), 4)}
            elif qtype == "score":
                levels = q.get("criteria") or []
                if not levels:
                    continue
                idx = int(u * len(levels))
                idx = min(idx, len(levels) - 1)
                probs = {str(i): round(0.9 if i == idx else 0.1 / max(1, len(levels) - 1), 4)
                         for i in range(len(levels))}
                answers[qid] = {"type": "score", "score": float(idx), "probabilities": probs,
                                "confidence": 0.8}
        # deterministic token estimate so cost accounting is exercised
        self._last_usage = {"input_tokens": max(1, len(str(state)) // 4 +
                                                 sum(len(json.dumps(q)) for q in questions.values()) // 4)}
        return normalise_answers(answers)


# ------------------------------------------------------------------ registry
def build_provider(spec: str) -> Provider:
    """spec examples: jev | jev:jev-1.14.0 | clef | clef:clef-flash | mock | oai"""
    name, _, arg = spec.partition(":")
    name = name.lower().strip()
    if name == "jev":
        return JevProvider(model=arg or "jev-latest")
    if name == "clef":
        return ClefProvider(model=arg or "clef-flash")
    if name == "mock":
        return MockProvider()
    if name == "oai":
        return OpenAICompatibleProvider(model=arg or None)
    raise ValueError(f"unknown provider spec: {spec!r} "
                     f"(try jev, clef, mock, oai)")


def available_providers() -> list[tuple[str, bool, str]]:
    """(spec, configured, note) for every provider the harness knows."""
    return [
        ("mock", True, "offline simulator - tests the harness, proves nothing about real models"),
        ("jev", bool(os.environ.get("TYPESAFE_API_KEY")),
         "TypeSafe Jev - needs TYPESAFE_API_KEY"),
        ("clef:clef-flash", bool(os.environ.get("CLOUDFLARE_ACCOUNT_ID") and
                                 os.environ.get("CLOUDFLARE_AUTH_TOKEN")),
         "Cloudflare clef-flash 9B - needs CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_AUTH_TOKEN"),
        ("clef:clef", bool(os.environ.get("CLOUDFLARE_ACCOUNT_ID") and
                           os.environ.get("CLOUDFLARE_AUTH_TOKEN")),
         "Cloudflare clef 27B (vision) - same env vars"),
        ("oai", bool(os.environ.get("OPENAI_BASE_URL") and os.environ.get("OPENAI_API_KEY")),
         "OpenAI-compatible (e.g. pplx-decider via OpenRouter) - needs OPENAI_* env vars"),
    ]
