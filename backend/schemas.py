from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RoleOut(BaseModel):
    id: int
    org_id: int
    title: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    is_board: bool
    is_current: bool
    org_name: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = super().from_orm(obj)
        data.org_name = obj.org.name if obj.org else None
        return data


class EducationOut(BaseModel):
    id: int
    institution: str
    degree: Optional[str]
    field: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]

    class Config:
        from_attributes = True


class PersonSummary(BaseModel):
    id: int
    full_name: str
    current_title: Optional[str]
    current_company: Optional[str]
    location: Optional[str]
    linkedin_url: Optional[str]
    is_internal: bool

    class Config:
        from_attributes = True


class PersonDetail(PersonSummary):
    email: Optional[str]
    bio: Optional[str]
    photo_url: Optional[str]
    roles: List[RoleOut] = []
    education: List[EducationOut] = []

    class Config:
        from_attributes = True


class PersonCreate(BaseModel):
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    is_internal: bool = False


class OrgSummary(BaseModel):
    id: int
    name: str
    linkedin_slug: Optional[str]
    hq_location: Optional[str]
    industry: Optional[str]
    is_portfolio: bool

    class Config:
        from_attributes = True


class OrgDetail(OrgSummary):
    domain: Optional[str]
    roles: List[RoleOut] = []

    class Config:
        from_attributes = True


class OrgCreate(BaseModel):
    name: str
    linkedin_slug: Optional[str] = None
    domain: Optional[str] = None
    hq_location: Optional[str] = None
    industry: Optional[str] = None
    is_portfolio: bool = False


class RoleCreate(BaseModel):
    person_id: int
    org_name: str
    title: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    is_board: bool = False


class EducationCreate(BaseModel):
    person_id: int
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class Signal(BaseModel):
    type: str
    label: str
    detail: str
    points: int
    icon: str


class ConnectorResult(BaseModel):
    sp_member: PersonSummary
    score: int
    strength: str  # strong | medium | weak
    signals: List[Signal]

    class Config:
        from_attributes = True


class ConnectivityResponse(BaseModel):
    target: PersonSummary
    connectors: List[ConnectorResult]

    class Config:
        from_attributes = True


class OverlapResult(BaseModel):
    sp_member: PersonSummary
    target_person: PersonSummary
    score: int
    strength: str
    signals: List[Signal]

    class Config:
        from_attributes = True


class CompanyConnectivityResponse(BaseModel):
    org: OrgSummary
    overlaps: List[OverlapResult]
    total: int

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    internal_person_id: int
    external_person_id: int
    interaction_type: str = "meeting"
    occurred_at: datetime
    notes: Optional[str] = None
    sentiment: int = 0


class InteractionOut(InteractionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
