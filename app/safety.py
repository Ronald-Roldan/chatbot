from __future__ import annotations

import re


def restricted_question(question: str) -> str | None:
    normalized = question.lower()
    patterns = [
        r"por qui[eé]n (debo |deber[ií]a )?votar", r"recomienda.*candidat", r"mejor candidat",
        r"ranking.*candidat", r"intenci[oó]n de voto", r"predi[cz].*elec", r"convence.*votar",
    ]
    if any(re.search(pattern, normalized) for pattern in patterns):
        return "El asistente no recomienda candidaturas, no predice elecciones ni intenta influir en el voto. Puede consultar propuestas documentadas de una candidatura o tema específico."
    return None
