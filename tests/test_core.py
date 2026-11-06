import json

from app import audit, documents
from app.config import ROLE_CLEARANCE, Settings
from app.ratelimit import RateLimiter
from app.retrieval import Index

S = Settings()
INDEX = Index(documents.load(S.docs_dir))


def test_retrieval_never_returns_documents_above_clearance():
    for q in ["salary bands 2026 band 4", "Jane Example mobile emergency contact", "HR-CONFIDENTIAL-7731"]:
        for c in INDEX.search(q, ROLE_CLEARANCE["employee"], k=10):
            assert c.label in ROLE_CLEARANCE["employee"]
    assert any(c.doc_id == "salary-bands" for c in INDEX.search("salary bands", ROLE_CLEARANCE["hr"]))


def test_poisoned_chunks_are_flagged_and_quarantined():
    flagged = {(c.doc_id, c.chunk_no) for c in INDEX.chunks if c.ingest_flags}
    assert ("supplier-faq", 2) in flagged and ("travel-policy", 2) in flagged
    hits = INDEX.search("suppliers paid immediately bank details", ROLE_CLEARANCE["employee"], k=10, exclude_flagged=True)
    assert all(not c.ingest_flags for c in hits)


def test_audit_chain_detects_tampering(tmp_audit):
    for i in range(3):
        audit.write(tmp_audit, {"n": i})
    assert audit.verify(tmp_audit) == (True, 3, "intact")
    lines = tmp_audit.read_text().splitlines()
    rec = json.loads(lines[1])
    rec["n"] = 99
    lines[1] = json.dumps(rec, sort_keys=True)
    tmp_audit.write_text("\n".join(lines) + "\n")
    ok, n, msg = audit.verify(tmp_audit)
    assert not ok and n == 2


def test_audit_detects_deleted_record(tmp_audit):
    for i in range(3):
        audit.write(tmp_audit, {"n": i})
    lines = tmp_audit.read_text().splitlines()
    tmp_audit.write_text(lines[0] + "\n" + lines[2] + "\n")
    assert audit.verify(tmp_audit)[0] is False


def test_rate_limiter():
    rl = RateLimiter(per_minute=3)
    assert [rl.allow("a") for _ in range(4)] == [True, True, True, False]
    assert rl.allow("b")
