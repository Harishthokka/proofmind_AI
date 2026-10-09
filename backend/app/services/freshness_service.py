import re
from typing import List, Dict, Any

class FreshnessService:
    DATE_PATTERNS = [
        r'\b(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})\b',  # 2026-01-15
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? 20\d{2}\b', # January 15, 2026
        r'\b(20\d{2})\b', # 2026
        r'\bv(\d+\.\d+)\b' # v1.2
    ]

    DATE_QUERY_TERMS = {'date', 'deadline', 'effective', 'version', 'freshness', 'outdated', 'current', 'latest', 'validity', 'year', 'when'}

    def extract_dates_and_versions(self, text: str) -> Dict[str, Any]:
        """Extracts date signatures and version strings from text."""
        dates = []
        versions = []
        for pattern in self.DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0]
                if 'v' in m.lower() or '.' in m:
                    versions.append(m)
                else:
                    dates.append(m)
        return {
            "dates": list(set(dates)),
            "versions": list(set(versions))
        }

    def evaluate_freshness(self, question: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assesses date and version metadata in the context of the user's question.
        Unrelated document dates do NOT automatically flag a date conflict for general factual questions.
        """
        if not documents:
            return {
                "rating": "UNCERTAIN",
                "score": 0.50,
                "note": "No source documents provided.",
                "date_conflict": False
            }

        doc_dates = []
        for doc in documents:
            filename = doc.get("filename", "")
            pages = doc.get("pages", [])
            sample_text = "\n".join([p.get("text", "") for p in pages[:2]])
            extracted = self.extract_dates_and_versions(sample_text)
            
            freshness_date = doc.get("freshness_date") or (extracted["dates"][0] if extracted["dates"] else "2026-01-15")
            version = extracted["versions"][0] if extracted["versions"] else doc.get("version", "v1.0")
            
            doc_dates.append({
                "filename": filename,
                "date": freshness_date,
                "version": version
            })

        # Determine if user's question is asking about dates, versions, or effective periods
        raw_words = set(re.findall(r'\b[a-zA-Z0-9_-]+\b', question.lower()))
        is_date_query = bool(raw_words.intersection(self.DATE_QUERY_TERMS))

        unique_dates = set(d["date"] for d in doc_dates)
        unique_versions = set(d["version"] for d in doc_dates)

        # Only flag date_conflict if question explicitly inquires about dates/versions AND documents variance exists
        if is_date_query and len(documents) > 1 and (len(unique_dates) > 1 or len(unique_versions) > 1):
            date_summary = ", ".join([f"'{d['filename']}' ({d['date']})" for d in doc_dates])
            return {
                "rating": "CONFLICTING_DATES",
                "score": 0.75,
                "note": f"Date/Version Variance Detected for date query: {date_summary}. Applicability is unresolved.",
                "date_conflict": True,
                "doc_dates": doc_dates
            }

        has_recent = any("2026" in d["date"] or "2025" in d["date"] for d in doc_dates)
        rating = "CURRENT" if has_recent else "OUTDATED"

        return {
            "rating": rating,
            "score": 0.95 if rating == "CURRENT" else 0.70,
            "note": "Document dates evaluated in question context.",
            "date_conflict": False,
            "doc_dates": doc_dates
        }

freshness_service = FreshnessService()
