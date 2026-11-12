"""SQLAlchemy models — a GRC-register shape (Risk / Control / Evidence /
Issue) plus Azure governance objects: AzureResource, AgentAction, Approval.
Swap the SQLite URL for PostgreSQL in production."""
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    title = Column(String)
    likelihood = Column(Integer)
    impact = Column(Integer)
    inherent_score = Column(Integer)
    category = Column(String)
    frameworks = Column(String)
    description = Column(Text)


class Control(Base):
    __tablename__ = "controls"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    title = Column(String)
    risk_code = Column(String)
    frameworks = Column(String)
    owner = Column(String)
    description = Column(Text)


class AzureResource(Base):
    __tablename__ = "azure_resources"
    id = Column(Integer, primary_key=True)
    resource_id = Column(String, unique=True)
    name = Column(String)
    kind = Column(String)  # subscription | resource_group | vm | storage | keyvault | ai | user | policy | defender
    resource_group = Column(String, nullable=True)
    region = Column(String, nullable=True)
    status = Column(String)  # compliant | non_compliant | review
    details = Column(Text)  # JSON
    owner = Column(String, nullable=True)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    control_code = Column(String)
    test_name = Column(String)
    result = Column(String)  # Pass / Fail / Partial
    sha256 = Column(String)
    details = Column(Text)  # JSON, includes run_at used for hashing
    created_at = Column(DateTime, server_default=func.now())


class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    control_code = Column(String)
    status = Column(String, default="Open")  # Open -> In Progress -> Verified -> Closed
    owner = Column(String)
    severity = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    approval_id = Column(String, unique=True)
    agent_id = Column(String)
    tool = Column(String)
    arguments = Column(Text)  # JSON
    reason = Column(String)
    status = Column(String, default="pending")  # pending | approved | denied
    decided_by = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AgentAction(Base):
    __tablename__ = "agent_actions"
    id = Column(Integer, primary_key=True)
    agent_id = Column(String)
    tool = Column(String)
    decision = Column(String)
    reason = Column(String)
    engine = Column(String)
    native_decision = Column(String, nullable=True)
    approval_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
