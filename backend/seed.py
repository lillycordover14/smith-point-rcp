"""
Seed the database with the real Smith Point Capital team.
Education corrected from LinkedIn search results.
LinkedIn URLs verified Feb 2026.
"""
from models import Person, Organization, Role, Education


SP_TEAM = [
    {
        "full_name": "Keith Block",
        "first_name": "Keith",
        "last_name": "Block",
        "linkedin_url": "https://www.linkedin.com/in/keith-block-516a1811/",
        "current_title": "Founder & CEO",
        "current_company": "Smith Point Capital",
        "location": "San Francisco, CA",
        "is_internal": True,
        "orgs": [
            {"name": "Oracle",              "slug": "oracle",         "start": 1986, "end": 2013, "board": False},
            {"name": "Salesforce",          "slug": "salesforce",     "start": 2013, "end": 2020, "board": True},
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2022, "end": None, "board": False},
        ],
        "education": [
            {"institution": "Carnegie Mellon University", "degree": "MS/BS", "start": 1980, "end": 1984},
        ],
    },
    {
        "full_name": "Burke Norton",
        "first_name": "Burke",
        "last_name": "Norton",
        "linkedin_url": "https://www.linkedin.com/in/burke-norton-121a1a2/",
        "current_title": "Co-founder & Managing Director",
        "current_company": "Smith Point Capital",
        "location": "San Francisco, CA",
        "is_internal": True,
        "orgs": [
            {"name": "Wilson Sonsini",      "slug": "wilson-sonsini",     "start": 1993, "end": 2006, "board": False},
            {"name": "Expedia",             "slug": "expedia",            "start": 2006, "end": 2010, "board": False},
            {"name": "Salesforce",          "slug": "salesforce",         "start": 2010, "end": 2020, "board": False},
            {"name": "Vista Equity Partners","slug": "vista-equity-partners","start": 2020, "end": 2022, "board": False},
            {"name": "Smith Point Capital", "slug": "smith-point-capital","start": 2022, "end": None,  "board": False},
        ],
        "education": [
            # LinkedIn shows UC Berkeley School of Law
            {"institution": "UC Berkeley School of Law", "degree": "JD", "start": 1989, "end": 1993},
        ],
    },
    {
        "full_name": "Christopher Lytle",
        "first_name": "Christopher",
        "last_name": "Lytle",
        "linkedin_url": "https://www.linkedin.com/in/chris-lytle-a8141a15/",
        "current_title": "Co-founder & Managing Director",
        "current_company": "Smith Point Capital",
        "location": "Old Greenwich, CT",
        "is_internal": True,
        "orgs": [
            {"name": "Longfellow Capital",  "slug": "longfellow-capital",  "start": 1995, "end": 2022, "board": False},
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2022, "end": None,  "board": False},
        ],
        "education": [
            # LinkedIn shows Lafayette College (corrected from Dartmouth)
            {"institution": "Lafayette College", "degree": "BA", "start": 1987, "end": 1991},
        ],
    },
    {
        "full_name": "John Cummings",
        "first_name": "John",
        "last_name": "Cummings",
        "linkedin_url": "https://www.linkedin.com/in/johncummings/",
        "current_title": "Managing Director, CFO/COO",
        "current_company": "Smith Point Capital",
        "location": "San Francisco, CA",
        "is_internal": True,
        "orgs": [
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2022, "end": None, "board": False},
        ],
        "education": [
            # LinkedIn shows Columbia Business School
            {"institution": "Columbia Business School", "degree": "MBA", "start": 1992, "end": 1994},
        ],
    },
    {
        "full_name": "Tyler Prince",
        "first_name": "Tyler",
        "last_name": "Prince",
        "linkedin_url": "https://www.linkedin.com/in/tyler-prince-210701/",
        "current_title": "Managing Director, Head of Value Creation",
        "current_company": "Smith Point Capital",
        "location": "Chicago, IL",
        "is_internal": True,
        "orgs": [
            {"name": "Salesforce",          "slug": "salesforce",         "start": 2004, "end": 2019, "board": False},
            {"name": "ServiceNow",          "slug": "servicenow",         "start": 2019, "end": 2023, "board": False},
            {"name": "Smith Point Capital", "slug": "smith-point-capital","start": 2023, "end": None,  "board": False},
        ],
        "education": [
            # LinkedIn shows University of Illinois at Urbana-Champaign (corrected from Duke)
            {"institution": "University of Illinois Urbana-Champaign", "degree": "BA", "start": 1993, "end": 1997},
        ],
    },
    {
        "full_name": "Brooke Kiley Slattery",
        "first_name": "Brooke",
        "last_name": "Kiley Slattery",
        "linkedin_url": "https://www.linkedin.com/in/brooke-kiley-slattery-7372949a/",
        "current_title": "Principal Investor",
        "current_company": "Smith Point Capital",
        "location": "New York, NY",
        "is_internal": True,
        "orgs": [
            {"name": "Goldman Sachs",       "slug": "goldman-sachs",       "start": 2012, "end": 2016, "board": False},
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2022, "end": None,  "board": False},
        ],
        "education": [
            # LinkedIn shows Wharton / UPenn (corrected from Harvard)
            {"institution": "University of Pennsylvania - The Wharton School", "degree": "BS", "start": 2008, "end": 2012},
        ],
    },
    {
        "full_name": "Lorenzo Salazar",
        "first_name": "Lorenzo",
        "last_name": "Salazar",
        "linkedin_url": "https://www.linkedin.com/in/lorenzosalazar16/",
        "current_title": "Principal Investor",
        "current_company": "Smith Point Capital",
        "location": "Austin, TX",
        "is_internal": True,
        "orgs": [
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2022, "end": None, "board": False},
        ],
        "education": [
            # LinkedIn shows UT Austin McCombs
            {"institution": "University of Texas at Austin", "degree": "MBA", "start": 2014, "end": 2016},
        ],
    },
    {
        "full_name": "Sewon Park",
        "first_name": "Sewon",
        "last_name": "Park",
        "linkedin_url": "https://www.linkedin.com/in/sewon-park-a939b9156/",
        "current_title": "Associate",
        "current_company": "Smith Point Capital",
        "location": "New York, NY",
        "is_internal": True,
        "orgs": [
            {"name": "Goldman Sachs",       "slug": "goldman-sachs",       "start": 2021, "end": 2022, "board": False},
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2022, "end": None,  "board": False},
        ],
        "education": [
            {"institution": "Harvard University", "degree": "BA", "start": 2017, "end": 2021},
        ],
    },
    {
        "full_name": "Katie Rodday",
        "first_name": "Katie",
        "last_name": "Rodday",
        "linkedin_url": "https://www.linkedin.com/in/katie-rodday-082071a/",
        "current_title": "Director of Operations",
        "current_company": "Smith Point Capital",
        "location": "Boston, MA",
        "is_internal": True,
        "orgs": [
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2022, "end": None, "board": False},
        ],
        "education": [
            # LinkedIn shows Stonehill College
            {"institution": "Stonehill College", "degree": "BA", "start": 2004, "end": 2008},
        ],
    },
    {
        "full_name": "Lilly Cordover",
        "first_name": "Lilly",
        "last_name": "Cordover",
        "linkedin_url": "https://www.linkedin.com/in/lillycordover/",
        "current_title": "Analyst",
        "current_company": "Smith Point Capital",
        "location": "New York, NY",
        "is_internal": True,
        "orgs": [
            {"name": "Fifth Wall",          "slug": "fifth-wall",          "start": 2023, "end": 2024, "board": False},
            {"name": "Smith Point Capital", "slug": "smith-point-capital", "start": 2024, "end": None,  "board": False},
        ],
        "education": [
            # LinkedIn shows McIntire School of Commerce (UVA)
            {"institution": "University of Virginia - McIntire School of Commerce", "degree": "BS", "start": 2019, "end": 2023},
        ],
    },
]

# Sample external people for demo lookups
SAMPLE_EXTERNALS = [
    {
        "full_name": "Marc Benioff",
        "linkedin_url": "https://www.linkedin.com/in/marcbenioff/",
        "current_title": "CEO & Chairman",
        "current_company": "Salesforce",
        "location": "San Francisco, CA",
        "is_internal": False,
        "orgs": [
            {"name": "Oracle",     "slug": "oracle",     "start": 1986, "end": 1999, "board": False},
            {"name": "Salesforce", "slug": "salesforce", "start": 1999, "end": None,  "board": True},
        ],
        "education": [
            {"institution": "University of Southern California", "degree": "BS", "start": 1982, "end": 1986},
        ],
    },
    {
        "full_name": "Bret Taylor",
        "linkedin_url": "https://www.linkedin.com/in/bret-taylor/",
        "current_title": "Chairman & Former Co-CEO",
        "current_company": "Salesforce",
        "location": "San Francisco, CA",
        "is_internal": False,
        "orgs": [
            {"name": "Google",     "slug": "google",     "start": 2003, "end": 2007, "board": False},
            {"name": "Facebook",   "slug": "facebook",   "start": 2009, "end": 2012, "board": False},
            {"name": "Salesforce", "slug": "salesforce", "start": 2016, "end": 2023, "board": True},
        ],
        "education": [
            {"institution": "Stanford University", "degree": "BS/MS", "start": 1999, "end": 2003},
        ],
    },
    {
        "full_name": "Patrick Collison",
        "linkedin_url": "https://www.linkedin.com/in/patrickcollison/",
        "current_title": "CEO & Co-founder",
        "current_company": "Stripe",
        "location": "San Francisco, CA",
        "is_internal": False,
        "orgs": [
            {"name": "Stripe", "slug": "stripe", "start": 2010, "end": None, "board": True},
        ],
        "education": [
            {"institution": "MIT", "degree": "Started", "start": 2007, "end": 2009},
        ],
    },
    {
        "full_name": "Sam Altman",
        "linkedin_url": "https://www.linkedin.com/in/sam-altman-1b5a7b/",
        "current_title": "CEO",
        "current_company": "OpenAI",
        "location": "San Francisco, CA",
        "is_internal": False,
        "orgs": [
            {"name": "Y Combinator", "slug": "y-combinator", "start": 2014, "end": 2019, "board": False},
            {"name": "OpenAI",       "slug": "openai",        "start": 2019, "end": None,  "board": True},
        ],
        "education": [
            {"institution": "Stanford University", "degree": "Started CS", "start": 2003, "end": 2005},
        ],
    },
    {
        "full_name": "Dhivya Suryadevara",
        "linkedin_url": "https://www.linkedin.com/in/dhivya-suryadevara/",
        "current_title": "CFO",
        "current_company": "Stripe",
        "location": "San Francisco, CA",
        "is_internal": False,
        "orgs": [
            {"name": "Goldman Sachs", "slug": "goldman-sachs", "start": 2001, "end": 2018, "board": False},
            {"name": "Stripe",        "slug": "stripe",         "start": 2021, "end": None,  "board": False},
        ],
        "education": [
            {"institution": "University of Michigan", "degree": "MBA", "start": 2001, "end": 2003},
        ],
    },
]


def seed_db(db):
    print("Seeding database...")

    # Upsert orgs
    org_cache = {}

    def get_or_create_org(name, slug):
        if name in org_cache:
            return org_cache[name]
        org = db.query(Organization).filter(Organization.name == name).first()
        if not org:
            org = Organization(name=name, linkedin_slug=slug)
            db.add(org)
            db.flush()
        org_cache[name] = org
        return org

    def seed_person(pdata):
        existing = db.query(Person).filter(Person.linkedin_url == pdata["linkedin_url"]).first()
        if existing:
            return existing

        person = Person(
            full_name=pdata["full_name"],
            first_name=pdata.get("first_name"),
            last_name=pdata.get("last_name"),
            linkedin_url=pdata.get("linkedin_url"),
            current_title=pdata.get("current_title"),
            current_company=pdata.get("current_company"),
            location=pdata.get("location"),
            is_internal=pdata.get("is_internal", False),
        )
        db.add(person)
        db.flush()

        for org_data in pdata.get("orgs", []):
            org = get_or_create_org(org_data["name"], org_data.get("slug"))
            role = Role(
                person_id=person.id,
                org_id=org.id,
                title=pdata.get("current_title") if org_data["end"] is None else None,
                start_year=org_data["start"],
                end_year=org_data["end"],
                is_board=org_data.get("board", False),
                is_current=org_data["end"] is None,
            )
            db.add(role)

        for edu_data in pdata.get("education", []):
            edu = Education(
                person_id=person.id,
                institution=edu_data["institution"],
                degree=edu_data.get("degree"),
                start_year=edu_data.get("start"),
                end_year=edu_data.get("end"),
            )
            db.add(edu)

        return person

    for pdata in SP_TEAM:
        seed_person(pdata)

    for pdata in SAMPLE_EXTERNALS:
        seed_person(pdata)

    db.commit()
    print(f"✅ Seeded {len(SP_TEAM)} SP team members + {len(SAMPLE_EXTERNALS)} sample externals")
