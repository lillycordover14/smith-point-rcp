from dataclasses import dataclass, field
from typing import List
from datetime import date
import math


@dataclass
class Signal:
    type: str
    label: str
    detail: str
    points: int
    icon: str


@dataclass
class ConnectivityResult:
    sp_member: object
    signals: List[Signal]
    score: int
    strength: str


def _school_normalize(name: str) -> str:
    return (name.lower()
        .replace("university", "").replace("college", "")
        .replace("school", "").replace("the ", "").replace("of ", "")
        .strip())


def _years_overlap(a_start, a_end, b_start, b_end) -> bool:
    if None in (a_start, a_end, b_start, b_end):
        return False
    return a_start <= b_end and b_start <= a_end


def _recency_decay(end_year: int) -> float:
    if end_year is None:
        return 1.0  # current role
    current_year = date.today().year
    years_ago = current_year - end_year
    if years_ago <= 3:
        return 1.0
    return max(0.4, 1.0 - 0.08 * (years_ago - 3))


def compute_connectivity(sp_member, target) -> ConnectivityResult:
    signals: List[Signal] = []
    seen_org_ids = set()

    sp_roles = list(sp_member.roles or [])
    t_roles  = list(target.roles or [])
    sp_edu   = list(sp_member.education or [])
    t_edu    = list(target.education or [])

    # ── 1. Company overlap ───────────────────────────────────────────────────
    for sr in sp_roles:
        if sr.is_board:
            continue
        for tr in t_roles:
            if tr.is_board:
                continue
            if sr.org_id != tr.org_id:
                continue
            if sr.org_id in seen_org_ids:
                continue

            # Calculate year overlap
            s_end = sr.end_year or date.today().year
            t_end = tr.end_year or date.today().year
            overlap_start = max(sr.start_year or 0, tr.start_year or 0)
            overlap_end   = min(s_end, t_end)
            overlap_years = max(0, overlap_end - overlap_start)

            if overlap_years < 0:
                continue

            pts = 30 * min(overlap_years / 3.0, 1.0) * _recency_decay(tr.end_year)
            pts = max(8, pts)  # floor: even 0-overlap same-company = 8pts

            label = f"Both worked at {sr.org.name}"
            detail = (
                f"{sp_member.full_name} ({sr.start_year}–{sr.end_year or 'present'}) and "
                f"{target.full_name} ({tr.start_year}–{tr.end_year or 'present'}) "
                f"both worked at {sr.org.name}"
            )
            if overlap_years > 0:
                detail += f" with {overlap_years} year(s) of overlap."
            else:
                detail += ", though at different times."

            signals.append(Signal("company", label, detail, int(pts), "🏢"))
            seen_org_ids.add(sr.org_id)

    # ── 2. Board overlap ─────────────────────────────────────────────────────
    sp_boards = {r.org_id for r in sp_roles if r.is_board}
    t_boards  = {r.org_id for r in t_roles  if r.is_board}
    for org_id in sp_boards & t_boards:
        org_name = next((r.org.name for r in sp_roles if r.org_id == org_id), str(org_id))
        signals.append(Signal(
            "board",
            f"Shared board seat at {org_name}",
            f"Both {sp_member.full_name} and {target.full_name} sit/sat on the {org_name} board.",
            20, "🪑"
        ))

    # ── 3. Education overlap ─────────────────────────────────────────────────
    for se in sp_edu:
        for te in t_edu:
            if _school_normalize(se.institution) != _school_normalize(te.institution):
                continue
            overlap = _years_overlap(se.start_year, se.end_year, te.start_year, te.end_year)
            pts = 20 if overlap else 12
            label = (
                f"Both attended {se.institution} at the same time"
                if overlap else f"Both attended {se.institution}"
            )
            if overlap:
                detail = (
                    f"{sp_member.full_name} ({se.start_year}–{se.end_year}) and "
                    f"{target.full_name} ({te.start_year}–{te.end_year}) "
                    f"overlapped at {se.institution}."
                )
            else:
                detail = (
                    f"{sp_member.full_name} attended {se.institution} ({se.start_year}–{se.end_year}); "
                    f"{target.full_name} attended {te.start_year}–{te.end_year}. "
                    f"No time overlap — different years."
                )
            signals.append(Signal("education", label, detail, pts, "🎓"))

    # ── 4. Location ──────────────────────────────────────────────────────────
    if sp_member.location and target.location:
        sp_city = sp_member.location.split(",")[0].strip().lower()
        t_city  = target.location.split(",")[0].strip().lower()
        if sp_city == t_city:
            signals.append(Signal(
                "location",
                f"Same location — {sp_member.location}",
                f"Both {sp_member.full_name} and {target.full_name} are based in {sp_member.location}.",
                5, "📍"
            ))

    # ── 5. Prior interactions ────────────────────────────────────────────────
    for interaction in getattr(sp_member, "interactions_as_internal", []):
        if interaction.external_person_id == target.id:
            months_ago = (date.today() - interaction.occurred_at.date()).days / 30
            pts = int(min(25, 25 * math.exp(-0.3 * months_ago)))
            signals.append(Signal(
                "interaction",
                f"Prior {interaction.interaction_type} ({interaction.occurred_at.strftime('%b %Y')})",
                f"{sp_member.full_name} had a {interaction.interaction_type} with {target.full_name} "
                f"in {interaction.occurred_at.strftime('%B %Y')}.",
                pts, "🤝"
            ))

    raw_score = sum(s.points for s in signals)
    score = min(100, raw_score)
    strength = "strong" if score >= 40 else "medium" if score >= 20 else "weak"

    return ConnectivityResult(sp_member=sp_member, signals=signals, score=score, strength=strength)
