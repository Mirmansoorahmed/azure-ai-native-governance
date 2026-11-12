"""Simulated Azure estate connector.

In a real tenant this module would be replaced by Azure Resource Graph
queries, Defender for Cloud API calls, Microsoft Graph (Entra ID) reads
and Azure OpenAI management-plane calls. The governance logic above
this layer would not change. All data here is synthetic (see data.py).
"""
from ..data import (
    AI_RESOURCES, DEFENDER, KEYVAULTS, POLICY_ASSIGNMENTS, RESOURCE_GROUPS,
    STORAGE, SUBSCRIPTION, USERS, VMS,
)


class SimulatedAzure:
    def subscription(self):
        return SUBSCRIPTION

    def resource_groups(self):
        return RESOURCE_GROUPS

    def vms(self):
        return VMS

    def storage_accounts(self):
        return STORAGE

    def keyvaults(self):
        return KEYVAULTS

    def ai_resources(self):
        return AI_RESOURCES

    def users(self):
        return USERS

    def policy_assignments(self):
        return POLICY_ASSIGNMENTS

    def defender(self):
        return DEFENDER

    def summary(self):
        return {
            "subscription": SUBSCRIPTION["name"],
            "resource_groups": len(RESOURCE_GROUPS),
            "vms_total": len(VMS),
            "vms_unencrypted": sum(1 for v in VMS if not v["disk_encrypted"]),
            "vms_public_ip": sum(1 for v in VMS if v["public_ip"]),
            "storage_total": len(STORAGE),
            "storage_public": sum(1 for s in STORAGE if s["public_blob"]),
            "storage_unencrypted": sum(1 for s in STORAGE if not s["encryption"]),
            "keyvaults_total": len(KEYVAULTS),
            "secrets_expired": sum(k["secrets_expired"] for k in KEYVAULTS),
            "ai_total": len(AI_RESOURCES),
            "ai_no_filter": sum(1 for a in AI_RESOURCES if not a["content_filter"]),
            "ai_outside_eu": sum(1 for a in AI_RESOURCES if a["data_residency"] != "EU"),
            "users_total": len(USERS),
            "users_no_mfa": sum(1 for u in USERS if not u["mfa"]),
            "users_no_ca": sum(1 for u in USERS if not u["ca_compliant"]),
            "users_missing_ai_literacy": sum(1 for u in USERS if not u["ai_literacy"]),
            "defender_secure_score_pct": DEFENDER["secure_score_pct"],
            "defender_high_findings": DEFENDER["recommendations_high"],
            "regions_outside_allowed": [g["name"] for g in RESOURCE_GROUPS if g["region"] not in ("germanywestcentral", "westeurope")],
        }
