"""PII detection and redaction with Microsoft Presidio, shared by GR-02 and the audit log."""
from __future__ import annotations

from functools import lru_cache

from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

ACCOUNT_PATTERN = r"\bBMT-\d{8}\b"
ENTITIES = ["US_SSN", "ACCOUNT_NUMBER", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"]


class PiiRedactor:
    def __init__(self) -> None:
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        })
        self._analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])
        self._analyzer.registry.add_recognizer(PatternRecognizer(
            supported_entity="ACCOUNT_NUMBER",
            patterns=[Pattern("brindlemoor_account", ACCOUNT_PATTERN, 0.9)]))
        self._anonymizer = AnonymizerEngine()

    def redact(self, text: str) -> tuple[str, list[str]]:
        """Return the text with PII replaced by <ENTITY_TYPE>, and the entity types found."""
        results = self._analyzer.analyze(text=text, entities=ENTITIES, language="en")
        if not results:
            return text, []
        redacted = self._anonymizer.anonymize(text=text, analyzer_results=results).text
        return redacted, sorted({r.entity_type for r in results})


@lru_cache(maxsize=1)
def get_redactor() -> PiiRedactor:
    return PiiRedactor()
