"""Seed the SQLite database with the simulated Azure estate (all synthetic)."""
import json

from .data import AI_RESOURCES, CONTROLS, KEYVAULTS, RISKS, STORAGE, VMS
from .database import Base, SessionLocal, engine
from .models import AzureResource, Control, Risk


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for r in RISKS:
            db.add(Risk(code=r["code"], title=r["title"], likelihood=r["likelihood"],
                        impact=r["impact"], inherent_score=r["likelihood"] * r["impact"],
                        category=r["category"], frameworks=r["frameworks"], description=r["description"]))
        for c in CONTROLS:
            db.add(Control(code=c["code"], title=c["title"], risk_code=c["risk_code"],
                           frameworks=c["frameworks"], owner=c["owner"], description=c["description"]))
        resources = []
        for v in VMS:
            resources.append(("vm", v["id"], v["name"], "rg-prod" if v["rg"] == "rg-prod" else v["rg"], v["region"],
                              "non_compliant" if (not v["disk_encrypted"] or v["public_ip"]) else "compliant", v, "Cloud Engineering"))
        for s in STORAGE:
            resources.append(("storage", s["id"], s["name"], s["rg"], s["region"],
                              "non_compliant" if (s["public_blob"] or not s["encryption"]) else "compliant", s, "Cloud Engineering"))
        for k in KEYVAULTS:
            resources.append(("keyvault", k["id"], k["name"], k["rg"], k["region"],
                              "non_compliant" if k["secrets_expired"] else "review", k, "Identity & Secrets"))
        for a in AI_RESOURCES:
            resources.append(("ai", a["id"], a["name"], a["rg"], a["region"],
                              "non_compliant" if not a["content_filter"] else "compliant", a, "AI Governance"))
        for kind, rid, name, rg, region, status, details, owner in resources:
            db.add(AzureResource(resource_id=rid, name=name, kind=kind, resource_group=rg,
                                 region=region, status=status, details=json.dumps(details), owner=owner))
        db.commit()
        print(f"Seeded: {len(RISKS)} risks, {len(CONTROLS)} controls, {len(resources)} Azure resources (SIMULATED data only)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
