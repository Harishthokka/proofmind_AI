import re
import uuid
from typing import List, Dict, Any
from app.schemas.analysis import EvidenceItem, EvidenceType

class ContradictionService:
    def detect_contradictions(
        self,
        question: str,
        retrieved_evidence: List[EvidenceItem],
        documents: List[Dict[str, Any]]
    ) -> List[EvidenceItem]:
        """
        Cross-examines ONLY retrieved evidence passages relevant to the current question (F04).
        Avoids false positives from unrelated document text or generic keyword pairs.
        """
        conflicts: List[EvidenceItem] = []

        if not retrieved_evidence or len(retrieved_evidence) < 2:
            return conflicts

        # Extract keywords from the question to scope comparison
        raw_q_words = re.findall(r'\b[a-zA-Z0-9_-]+\b', question.lower())
        stop_words = {'what', 'when', 'where', 'which', 'who', 'how', 'why', 'does', 'that', 'this', 'with', 'from', 'have', 'were', 'been', 'is', 'the', 'are', 'a', 'an', 'in', 'on', 'of', 'for', 'to', 'and', 'or', 'it'}
        q_topics = [w for w in raw_q_words if len(w) > 2 and w not in stop_words]

        # Group retrieved evidence items by document filename
        ev_by_doc: Dict[str, List[EvidenceItem]] = {}
        for ev in retrieved_evidence:
            ev_by_doc.setdefault(ev.source_filename, []).append(ev)

        # Need at least two different documents with relevant evidence to have a cross-document conflict
        doc_names = list(ev_by_doc.keys())
        if len(doc_names) < 2:
            return conflicts

        # Compare relevant retrieved evidence passages between different documents
        for i in range(len(retrieved_evidence)):
            for j in range(i + 1, len(retrieved_evidence)):
                ev1 = retrieved_evidence[i]
                ev2 = retrieved_evidence[j]

                # Only compare evidence coming from different documents
                if ev1.source_filename == ev2.source_filename:
                    continue

                t1_lower = ev1.passage.lower()
                t2_lower = ev2.passage.lower()

                # Verify both passages pertain to the question topic
                topic_match_1 = any(t in t1_lower for t in q_topics) if q_topics else True
                topic_match_2 = any(t in t2_lower for t in q_topics) if q_topics else True

                if not (topic_match_1 and topic_match_2):
                    continue

                # Extract numerical values and percentages (e.g. "75%", "80 percent", "75", "80")
                nums1 = re.findall(r'\b\d+(?:\s*%|\s*percent)?\b', t1_lower)
                nums2 = re.findall(r'\b\d+(?:\s*%|\s*percent)?\b', t2_lower)

                # Exclude standalone 4-digit years (e.g. 2024, 2025, 2026) to focus on policy values
                policy_nums1 = set([n for n in nums1 if not (len(n) == 4 and n.startswith(('202', '201')))])
                policy_nums2 = set([n for n in nums2 if not (len(n) == 4 and n.startswith(('202', '201')))])

                num_conflict = False
                if policy_nums1 and policy_nums2 and policy_nums1 != policy_nums2:
                    num_conflict = True

                # Check for opposing rule terms on the same topic (e.g., mandatory vs optional for the SAME subject)
                rule_conflict = False
                opposing_pairs = [('must', 'optional'), ('required', 'optional'), ('mandatory', 'optional'), ('prohibited', 'permitted')]
                for term1, term2 in opposing_pairs:
                    if (term1 in t1_lower and term2 in t2_lower) or (term2 in t1_lower and term1 in t2_lower):
                        rule_conflict = True
                        break

                if num_conflict or rule_conflict:
                    conflicts.append(
                        EvidenceItem(
                            id=f"ev-conflict-1-{uuid.uuid4().hex[:6]}",
                            source_filename=ev1.source_filename,
                            page_number=ev1.page_number,
                            source_date=ev1.source_date,
                            passage=ev1.passage,
                            type=EvidenceType.CONFLICTING,
                            confidence_score=0.90,
                            citation_verified=True,
                            verification_note=f"Conflicting source 1 regarding '{question}'"
                        )
                    )
                    conflicts.append(
                        EvidenceItem(
                            id=f"ev-conflict-2-{uuid.uuid4().hex[:6]}",
                            source_filename=ev2.source_filename,
                            page_number=ev2.page_number,
                            source_date=ev2.source_date,
                            passage=ev2.passage,
                            type=EvidenceType.CONFLICTING,
                            confidence_score=0.90,
                            citation_verified=True,
                            verification_note=f"Conflicting source 2 regarding '{question}'"
                        )
                    )
                    break

        return conflicts[:3]

contradiction_service = ContradictionService()
