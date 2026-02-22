"""
Smith Point Capital — Connection Finder Backend
Run: python server.py
Then open http://localhost:8000 in your browser.

No API keys needed. Uses DuckDuckGo to find company leadership
from public LinkedIn data.
"""

import re
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from duckduckgo_search import DDGS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sp-finder")

app = FastAPI(title="Smith Point Connection Finder")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── MODELS ────────────────────────────────────────────────────────────────

class CompanyRequest(BaseModel):
    url: str  # LinkedIn company URL

class Person(BaseModel):
    id: str
    name: str
    title: str
    orgs: list[str] = []
    education: list[dict] = []
    board: list[str] = []
    location: str = ""
    linkedin: str = ""

class CompanyResult(BaseModel):
    company_name: str
    people: list[Person]
    search_queries_used: int = 0

# ─── HELPERS ───────────────────────────────────────────────────────────────

def extract_company_slug(url: str) -> Optional[str]:
    """Pull company slug from LinkedIn URL."""
    m = re.search(r"linkedin\.com/company/([^/?#\s]+)", url)
    return m.group(1).rstrip("/") if m else None

def slug_to_name(slug: str) -> str:
    """Convert 'my-company-inc' → 'My Company Inc'."""
    return re.sub(r"-+", " ", slug).title()

def parse_linkedin_title(title_str: str) -> tuple[str, str]:
    """
    Parse a DuckDuckGo result title like:
    'John Smith - CEO at Acme Corp | LinkedIn'
    → ('John Smith', 'CEO at Acme Corp')
    """
    # Remove trailing '| LinkedIn' or '- LinkedIn'
    cleaned = re.sub(r"\s*[\|\-–—]\s*LinkedIn\s*$", "", title_str, flags=re.IGNORECASE).strip()
    # Split on first ' - ' or ' – ' or ' — '
    parts = re.split(r"\s*[\-–—]\s*", cleaned, maxsplit=1)
    name = parts[0].strip()
    title = parts[1].strip() if len(parts) > 1 else ""
    # Clean up name — remove anything in parens, extra whitespace
    name = re.sub(r"\s*\(.*?\)\s*", " ", name).strip()
    # Skip if name looks like a company name or is too long
    if len(name.split()) > 5 or not name:
        return "", ""
    return name, title

def extract_orgs_from_text(text: str, company_name: str) -> list[str]:
    """Pull company names from a search snippet."""
    orgs = set()
    # Add the target company itself
    orgs.add(company_name)
    
    # Known SP-relevant companies to look for
    sp_companies = [
        "Salesforce", "Oracle", "Snowflake", "ServiceNow", "Databricks",
        "Vista Equity Partners", "Morgan Stanley", "Credit Suisse", "Goldman Sachs",
        "Insight Partners", "VMG Partners", "PwC", "PricewaterhouseCoopers",
        "IBM", "PeopleSoft", "Cisco", "Microsoft", "Twilio", "Datadog",
        "Stripe", "McKinsey", "Booz Allen Hamilton", "Booz Allen",
        "Heidrick & Struggles", "SAP", "Genesys", "Confluent", "Anthropic",
        "Procter & Gamble", "P&G", "Expedia", "Wilson Sonsini", "Celonis",
        "ExactTarget", "Diligent", "Andersen Consulting", "Accenture",
        "Ionic Partners", "Fifth Wall", "Longfellow Capital",
        "Osterweis", "Inseego", "Cavulus", "Umee",
        "Google", "Amazon", "Meta", "Apple", "Netflix",
        "Uber", "Airbnb", "Tesla", "SpaceX", "Palantir",
        "Workday", "Splunk", "VMware", "Dell", "HP", "Intel",
        "Qualcomm", "Adobe", "Zoom", "Slack", "HubSpot",
        "JP Morgan", "JPMorgan", "Bank of America", "Citigroup", "Citi",
        "Deloitte", "EY", "Ernst & Young", "KPMG", "Bain",
        "BCG", "Boston Consulting", "Sequoia", "Andreessen Horowitz", "a16z",
        "Kleiner Perkins", "Benchmark", "Lightspeed", "GV", "Tiger Global",
        "SoftBank", "Thoma Bravo", "Silver Lake", "KKR", "Blackstone",
        "General Atlantic", "Warburg Pincus", "Bessemer",
    ]
    
    text_lower = text.lower()
    for co in sp_companies:
        if co.lower() in text_lower:
            orgs.add(co)
    
    # Also try to find "at CompanyName" or "Company Name" patterns
    # "Previously at X" or "Experience: X, Y, Z"
    prev_patterns = [
        r"(?:previously|formerly|former)\s+(?:at|with|@)\s+([A-Z][A-Za-z\s&.]+?)(?:\s*[,;.|]|\s+and\s)",
        r"(?:experience|worked at|career)[:.]?\s*([A-Z][A-Za-z\s&.,]+?)(?:\s*[|])",
    ]
    for pat in prev_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            candidates = re.split(r"\s*[,;]\s*", m.group(1))
            for c in candidates:
                c = c.strip()
                if 2 <= len(c) <= 40 and c[0].isupper():
                    orgs.add(c)
    
    return list(orgs)

def extract_education_from_text(text: str) -> list[dict]:
    """Pull school names from search snippets."""
    schools = []
    known_schools = [
        "Carnegie Mellon", "Wharton", "UPenn", "University of Pennsylvania",
        "Columbia Business School", "Columbia University", "UC Berkeley", "Berkeley",
        "Haas School", "UCLA", "University of Illinois", "UIUC",
        "UT Austin", "University of Texas", "McCombs",
        "Lafayette College", "Stonehill College", "University of Virginia", "UVA",
        "McIntire", "Stanford", "Harvard", "MIT", "Yale", "Princeton",
        "Northwestern", "Kellogg", "Booth", "Chicago Booth",
        "Duke", "Fuqua", "NYU", "Stern", "Georgetown",
        "Cornell", "Dartmouth", "Tuck", "Brown", "Penn State",
        "Michigan", "Ross", "Darden", "Sloan",
    ]
    text_lower = text.lower()
    for sch in known_schools:
        if sch.lower() in text_lower:
            schools.append({"s": sch, "y": None})
    return schools

def extract_location_from_text(text: str) -> str:
    """Try to find location from snippet."""
    loc_patterns = [
        r"(?:Location|Based in|located in)[:\s]+([A-Z][A-Za-z\s]+,\s*[A-Z]{2})",
        r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?,\s*(?:CA|NY|TX|IL|CT|MA|WA|CO|GA|FL|VA|PA|NJ|DC))\b",
    ]
    for pat in loc_patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()
    return ""


# ─── SEARCH ENGINE ─────────────────────────────────────────────────────────

def search_ddg(query: str, max_results: int = 15) -> list[dict]:
    """Run a DuckDuckGo search and return results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        log.warning(f"DDG search failed for '{query}': {e}")
        return []

def find_company_people(company_name: str, linkedin_slug: str) -> tuple[list[Person], int]:
    """
    Search DuckDuckGo for all leadership at a company.
    Returns (people, num_queries).
    """
    all_results = []
    queries_used = 0
    
    # Multiple targeted searches to find different roles
    search_queries = [
        f'site:linkedin.com/in "{company_name}" CEO OR "Chief Executive" OR founder OR co-founder',
        f'site:linkedin.com/in "{company_name}" CTO OR CFO OR COO OR CRO OR CMO OR "Chief"',
        f'site:linkedin.com/in "{company_name}" "board of directors" OR "board member" OR director OR advisor',
        f'site:linkedin.com/in "{company_name}" VP OR SVP OR EVP OR "Vice President" OR president',
        f'site:linkedin.com/in "{company_name}" "General Counsel" OR CHRO OR CPO OR "Head of"',
    ]
    
    for query in search_queries:
        results = search_ddg(query, max_results=12)
        all_results.extend(results)
        queries_used += 1
        log.info(f"Query: {query[:80]}... → {len(results)} results")
    
    # De-duplicate by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        url = r.get("href", "")
        if url and url not in seen_urls and "linkedin.com/in/" in url:
            seen_urls.add(url)
            unique_results.append(r)
    
    log.info(f"Found {len(unique_results)} unique LinkedIn profiles for {company_name}")
    
    # Parse each result into a Person
    people_map = {}  # name_lower → Person
    for r in unique_results:
        title_str = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        
        name, role = parse_linkedin_title(title_str)
        if not name or len(name) < 3:
            continue
        
        # Skip if this doesn't seem related to our company
        combined_text = f"{title_str} {body}".lower()
        if company_name.lower() not in combined_text and linkedin_slug.lower().replace("-", " ") not in combined_text:
            continue
        
        name_key = name.lower().strip()
        
        if name_key in people_map:
            # Merge info
            existing = people_map[name_key]
            new_orgs = extract_orgs_from_text(f"{title_str} {body}", company_name)
            existing.orgs = list(set(existing.orgs + new_orgs))
            new_edu = extract_education_from_text(body)
            existing.education = existing.education + [e for e in new_edu if e not in existing.education]
            if not existing.location:
                existing.location = extract_location_from_text(body)
        else:
            orgs = extract_orgs_from_text(f"{title_str} {body}", company_name)
            edu = extract_education_from_text(body)
            loc = extract_location_from_text(body)
            
            people_map[name_key] = Person(
                id=f"t-{len(people_map)}",
                name=name,
                title=role or f"Executive at {company_name}",
                orgs=orgs,
                education=edu,
                board=[],
                location=loc,
                linkedin=href,
            )
    
    people = list(people_map.values())
    
    # Now do deep-dive searches on each person to find more career detail
    for person in people[:20]:  # Cap at 20 people for speed
        detail_results = search_ddg(
            f'"{person.name}" site:linkedin.com/in',
            max_results=3,
        )
        queries_used += 1
        
        for dr in detail_results:
            body = dr.get("body", "")
            title = dr.get("title", "")
            combined = f"{title} {body}"
            
            # Extract more orgs
            new_orgs = extract_orgs_from_text(combined, company_name)
            person.orgs = list(set(person.orgs + new_orgs))
            
            # Extract education
            new_edu = extract_education_from_text(combined)
            for e in new_edu:
                if e not in person.education:
                    person.education.append(e)
            
            # Extract location
            if not person.location:
                person.location = extract_location_from_text(combined)
    
    log.info(f"Final: {len(people)} people with career details, {queries_used} queries used")
    return people, queries_used


# ─── API ROUTES ────────────────────────────────────────────────────────────

@app.post("/api/find-connections", response_model=CompanyResult)
async def find_connections(req: CompanyRequest):
    """Main endpoint: takes LinkedIn company URL, returns leadership with career data."""
    slug = extract_company_slug(req.url)
    if not slug:
        raise HTTPException(400, "Invalid LinkedIn company URL. Expected: linkedin.com/company/...")
    
    company_name = slug_to_name(slug)
    log.info(f"Starting search for: {company_name} (slug: {slug})")
    
    # Run the search (this takes 20-60 seconds)
    loop = asyncio.get_event_loop()
    people, queries_used = await loop.run_in_executor(
        None, find_company_people, company_name, slug
    )
    
    if not people:
        # Try alternate search with just the slug
        log.info(f"No results with name, trying slug: {slug}")
        people, q2 = await loop.run_in_executor(
            None, find_company_people, slug.replace("-", " "), slug
        )
        queries_used += q2
    
    return CompanyResult(
        company_name=company_name,
        people=people,
        search_queries_used=queries_used,
    )

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Smith Point Connection Finder is running"}

# ─── SERVE FRONTEND ───────────────────────────────────────────────────────

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_dir / "index.html")
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


# ─── RUN ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  Smith Point Capital — Connection Finder")
    print("="*60)
    print(f"\n  Open in browser: http://localhost:8000")
    print(f"  API docs:        http://localhost:8000/docs")
    print(f"\n  No API keys needed. Using DuckDuckGo for search.")
    print(f"  Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
