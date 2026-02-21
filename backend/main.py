from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import math

from database import get_db, engine
import models, schemas, scoring
from seed import seed_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smith Point RCP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db = next(get_db())
    if db.query(models.Person).filter(models.Person.is_internal == True).count() == 0:
        seed_db(db)
    db.close()

# ── People ──────────────────────────────────────────────────────────────────

@app.get("/api/people", response_model=List[schemas.PersonSummary])
def list_people(q: Optional[str] = None, internal_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Person)
    if internal_only:
        query = query.filter(models.Person.is_internal == True)
    if q:
        query = query.filter(
            models.Person.full_name.ilike(f"%{q}%") |
            models.Person.current_company.ilike(f"%{q}%")
        )
    return query.order_by(models.Person.full_name).limit(50).all()

@app.get("/api/people/{person_id}", response_model=schemas.PersonDetail)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@app.post("/api/people", response_model=schemas.PersonDetail)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = models.Person(**person.dict(exclude={"orgs", "education"}))
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

# ── Organizations ────────────────────────────────────────────────────────────

@app.get("/api/orgs", response_model=List[schemas.OrgSummary])
def list_orgs(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Organization)
    if q:
        query = query.filter(models.Organization.name.ilike(f"%{q}%"))
    return query.order_by(models.Organization.name).limit(50).all()

@app.get("/api/orgs/{org_id}", response_model=schemas.OrgDetail)
def get_org(org_id: int, db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.post("/api/orgs", response_model=schemas.OrgSummary)
def create_org(org: schemas.OrgCreate, db: Session = Depends(get_db)):
    db_org = models.Organization(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

# ── Connectivity ─────────────────────────────────────────────────────────────

@app.get("/api/connectivity", response_model=schemas.ConnectivityResponse)
def get_connectivity(target_id: int, db: Session = Depends(get_db)):
    target = db.query(models.Person).filter(models.Person.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target person not found")

    sp_members = db.query(models.Person).filter(models.Person.is_internal == True).all()
    results = []
    for member in sp_members:
        result = scoring.compute_connectivity(member, target)
        if result.signals:
            results.append(result)

    results.sort(key=lambda x: x.score, reverse=True)
    return schemas.ConnectivityResponse(target=target, connectors=results)

@app.get("/api/connectivity/company", response_model=schemas.CompanyConnectivityResponse)
def get_company_connectivity(linkedin_slug: str, db: Session = Depends(get_db)):
    # Find or look up people at this org
    org = db.query(models.Organization).filter(
        models.Organization.linkedin_slug == linkedin_slug
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail=f"Company '{linkedin_slug}' not found. Add it via POST /api/orgs first.")

    # Get all people at this org
    roles = db.query(models.Role).filter(models.Role.org_id == org.id).all()
    people_ids = list(set(r.person_id for r in roles))
    target_people = db.query(models.Person).filter(
        models.Person.id.in_(people_ids),
        models.Person.is_internal == False
    ).all()

    if not target_people:
        raise HTTPException(status_code=404, detail=f"No external people found at '{org.name}'.")

    sp_members = db.query(models.Person).filter(models.Person.is_internal == True).all()

    overlaps = []
    for target in target_people:
        for member in sp_members:
            result = scoring.compute_connectivity(member, target)
            if result.signals:
                overlaps.append(schemas.OverlapResult(
                    sp_member=member,
                    target_person=target,
                    score=result.score,
                    strength=result.strength,
                    signals=result.signals,
                ))

    overlaps.sort(key=lambda x: x.score, reverse=True)
    return schemas.CompanyConnectivityResponse(org=org, overlaps=overlaps, total=len(overlaps))

# ── Roles ────────────────────────────────────────────────────────────────────

@app.post("/api/roles", response_model=schemas.RoleOut)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    # Upsert org by name
    org = db.query(models.Organization).filter(
        models.Organization.name.ilike(role.org_name)
    ).first()
    if not org:
        org = models.Organization(name=role.org_name)
        db.add(org)
        db.commit()
        db.refresh(org)

    db_role = models.Role(
        person_id=role.person_id,
        org_id=org.id,
        title=role.title,
        start_year=role.start_year,
        end_year=role.end_year,
        is_board=role.is_board,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# ── Education ────────────────────────────────────────────────────────────────

@app.post("/api/education", response_model=schemas.EducationOut)
def create_education(edu: schemas.EducationCreate, db: Session = Depends(get_db)):
    db_edu = models.Education(**edu.dict())
    db.add(db_edu)
    db.commit()
    db.refresh(db_edu)
    return db_edu

# ── Interactions ─────────────────────────────────────────────────────────────

@app.get("/api/interactions", response_model=List[schemas.InteractionOut])
def list_interactions(person_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Interaction)
    if person_id:
        query = query.filter(
            (models.Interaction.internal_person_id == person_id) |
            (models.Interaction.external_person_id == person_id)
        )
    return query.order_by(models.Interaction.occurred_at.desc()).limit(100).all()

@app.post("/api/interactions", response_model=schemas.InteractionOut)
def create_interaction(interaction: schemas.InteractionCreate, db: Session = Depends(get_db)):
    db_interaction = models.Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
