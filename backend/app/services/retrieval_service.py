import re
import uuid
from typing import List, Dict, Any, Set
from app.schemas.analysis import EvidenceItem, EvidenceType

class RetrievalService:
    SYNONYM_MAP = {
        "characteristics": {"characteristics", "characteristic", "vs", "v", "features", "properties", "dimensions", "attributes", "pillars", "aspects"},
        "vs": {"vs", "v", "characteristics", "characteristic", "features", "properties", "dimensions", "attributes"},
        "v": {"vs", "v", "characteristics", "characteristic", "features", "properties", "dimensions"},
        "quality": {"quality", "validation", "cleaning", "verification", "checks", "check", "integrity", "accuracy"},
        "checks": {"checks", "check", "validation", "verification", "audits", "audit", "rules", "testing", "controls"},
        "attendance": {"attendance", "present", "absent", "presence"},
        "requirement": {"requirement", "requirements", "policy", "rule", "mandatory", "must", "minimum", "required"},
        "recommended": {"recommended", "recommendation", "suggested", "advised", "best", "practices"},
    }

    STOP_WORDS = {
        'what', 'when', 'where', 'which', 'who', 'how', 'why', 'does', 'that', 'this',
        'with', 'from', 'have', 'were', 'been', 'is', 'the', 'are', 'a', 'an', 'in',
        'on', 'of', 'for', 'to', 'and', 'or', 'it', 'explain', 'tell', 'me', 'about',
        'can', 'you', 'give', 'list', 'show'
    }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z0-9_-]+\b', text.lower())

    def _get_expanded_keywords(self, tokens: List[str]) -> Set[str]:
        expanded = set()
        for tok in tokens:
            if tok in self.STOP_WORDS or len(tok) <= 1:
                continue
            expanded.add(tok)
            # Add simple stemming (e.g. checks -> check)
            if tok.endswith('s') and len(tok) > 3:
                expanded.add(tok[:-1])
            if tok.endswith('es') and len(tok) > 4:
                expanded.add(tok[:-2])
            if tok.endswith('ing') and len(tok) > 4:
                expanded.add(tok[:-3])

            # Synonym expansion
            if tok in self.SYNONYM_MAP:
                expanded.update(self.SYNONYM_MAP[tok])
        return expanded

    def _extract_chunks(self, text: str) -> List[str]:
        """
        Extracts meaningful passages using paragraph and sliding window sentence chunking
        to prevent splitting relevant context across chunk boundaries.
        """
        if not text:
            return []

        # Split into paragraphs first
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n+', text) if len(p.strip()) > 10]
        
        chunks = []
        for p in paragraphs:
            chunks.append(p)
            # Split paragraph into sentences
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', p) if len(s.strip()) > 10]
            if len(sentences) > 1:
                for s in sentences:
                    chunks.append(s)
                # Combine adjacent sentence pairs for sliding window
                for i in range(len(sentences) - 1):
                    window = f"{sentences[i]} {sentences[i+1]}"
                    chunks.append(window)

        # Fallback if no paragraph structure found
        if not chunks:
            raw = [c.strip() for c in re.split(r'\n+|\. |\; ', text) if len(c.strip()) > 8]
            chunks = raw

        # Deduplicate while preserving order
        seen = set()
        dedup_chunks = []
        for c in chunks:
            if c not in seen and len(c) >= 15:
                seen.add(c)
                dedup_chunks.append(c)

        return dedup_chunks

    def retrieve_evidence(self, question: str, documents: List[Dict[str, Any]]) -> List[EvidenceItem]:
        """
        Extracts, scores, and ranks relevant evidence passages across multiple uploaded PDFs.
        Supports synonym matching, semantic concept expansion, and minimum relevance thresholding.
        """
        evidence_list: List[EvidenceItem] = []
        if not documents or not question.strip():
            return evidence_list

        q_tokens = self._tokenize(question)
        content_q_tokens = [t for t in q_tokens if t not in self.STOP_WORDS and len(t) > 1]

        if not content_q_tokens:
            return evidence_list

        expanded_q_keywords = self._get_expanded_keywords(q_tokens)
        q_lower = question.lower().strip()

        # Identify key named entities/distinctive terms in query (e.g., "apache", "spark", "5", "five")
        distinctive_terms = [t for t in content_q_tokens if len(t) > 3 or t.isdigit()]

        scored_candidates = []

        for doc in documents:
            filename = doc.get("filename", "document.pdf")
            freshness = doc.get("freshness_date", "2026-01-15")
            pages = doc.get("pages", [])

            for page in pages:
                page_num = page.get("page_number", 1)
                text = page.get("text", "").strip()
                if not text:
                    continue

                chunks = self._extract_chunks(text)

                for chunk in chunks:
                    chunk_lower = chunk.lower()
                    chunk_tokens = set(self._tokenize(chunk))

                    # 1. Direct content keyword match count
                    direct_matches = sum(1 for kw in content_q_tokens if kw in chunk_tokens or kw in chunk_lower)

                    # 2. Expanded/Synonym match count
                    expanded_matches = sum(1 for kw in expanded_q_keywords if kw in chunk_tokens or kw in chunk_lower)

                    # 3. Phrase match bonus
                    phrase_match = 2.0 if q_lower in chunk_lower else 0.0

                    # 4. Mandatory term check for query-specific entities
                    if len(content_q_tokens) >= 3:
                        # Generic background terms that shouldn't alone justify retrieval if core entity terms are missing
                        generic_terms = {'scholarship', 'university', 'document', 'policy', 'general', 'about', 'would', 'could', 'course', 'system'}
                        specific_q_terms = [t for t in content_q_tokens if t not in generic_terms]
                        if specific_q_terms:
                            found_specific = any(st in chunk_lower or st in chunk_tokens for st in specific_q_terms)
                            if not found_specific and direct_matches < 2:
                                continue

                    # Total relevance score
                    raw_score = (direct_matches * 1.5) + (expanded_matches * 0.8) + phrase_match

                    # Strict relevance threshold: require meaningful overlap
                    if raw_score >= 1.8 or (direct_matches >= 1 and expanded_matches >= 2):
                        confidence = min(0.98, round(0.65 + (raw_score * 0.08), 2))
                        
                        scored_candidates.append({
                            "score": raw_score,
                            "confidence": confidence,
                            "evidence": EvidenceItem(
                                id=f"ev-{uuid.uuid4().hex[:8]}",
                                source_filename=filename,
                                page_number=page_num,
                                source_date=freshness,
                                passage=chunk[:800],
                                type=EvidenceType.SUPPORTING,
                                confidence_score=confidence,
                                citation_verified=True,
                                verification_note=f"Verified on page {page_num} of {filename}"
                            )
                        })

        # Sort all candidates by score
        scored_candidates.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)

        # Group candidates by document filename to ensure multi-document candidate representation
        cands_by_doc: Dict[str, List[Dict[str, Any]]] = {}
        for cand in scored_candidates:
            doc_fn = cand["evidence"].source_filename
            cands_by_doc.setdefault(doc_fn, []).append(cand)

        # Select top candidates per document (up to 3 per document) to guarantee all relevant uploaded PDFs are evaluated
        selected_candidates = []
        for doc_fn, doc_cands in cands_by_doc.items():
            doc_cands.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)
            selected_candidates.extend(doc_cands[:3])

        # Sort selected multi-document candidates by relevance score descending
        selected_candidates.sort(key=lambda x: (x["score"], x["confidence"]), reverse=True)

        # Deduplicate while preserving multi-document representation
        seen_passages = set()
        final_evidence = []
        for cand in selected_candidates:
            pass_text = cand["evidence"].passage.strip()
            if pass_text not in seen_passages:
                seen_passages.add(pass_text)
                final_evidence.append(cand["evidence"])
                if len(final_evidence) >= 8:
                    break

        return final_evidence

retrieval_service = RetrievalService()

