"""The optional LLM layer must never break the app: on any error it falls back
to the deterministic rule-engine draft."""
import noordesk.llm as llm
import noordesk.local_llm as local_llm
from noordesk.pipeline import process_message


def test_llm_disabled_uses_rule_engine(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rec = process_message({"id": "a", "sender": "s", "raw_text": "I want to book"}, use_llm=True)
    assert rec["engine_used"] == "rule"
    assert rec["suggested_reply"]


def test_llm_exception_falls_back(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    # force the LLM call to blow up
    monkeypatch.setattr(llm, "_client", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    rec = process_message({"id": "b", "sender": "s", "raw_text": "I want to book"}, use_llm=True)
    assert rec["engine_used"] == "rule"          # fell back, no crash
    assert rec["suggested_reply"]


def test_llm_success_marks_engine(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(llm, "refine_reply", lambda text, lang, draft, context="": "POLISHED REPLY")
    rec = process_message({"id": "c", "sender": "s", "raw_text": "I want to book"}, use_llm=True)
    assert rec["engine_used"] == "llm"
    assert rec["suggested_reply"] == "POLISHED REPLY"


def test_local_ai_preferred_and_marks_engine(monkeypatch):
    # Local offline model takes precedence over cloud when available.
    monkeypatch.setattr(local_llm, "is_enabled", lambda: True)
    monkeypatch.setattr(local_llm, "refine_reply", lambda text, lang, draft, context="": "LOCAL DRAFT")
    rec = process_message({"id": "d", "sender": "s", "raw_text": "I want to book"}, use_llm=True)
    assert rec["engine_used"] == "local"
    assert rec["suggested_reply"] == "LOCAL DRAFT"


def test_local_ai_failure_falls_back_to_rule(monkeypatch):
    monkeypatch.setattr(local_llm, "is_enabled", lambda: True)
    monkeypatch.setattr(local_llm, "refine_reply", lambda text, lang, draft, context="": None)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rec = process_message({"id": "e", "sender": "s", "raw_text": "I want to book"}, use_llm=True)
    assert rec["engine_used"] == "rule"
    assert rec["suggested_reply"]
