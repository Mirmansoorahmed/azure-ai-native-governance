from app.policy import classify_use_case, evaluate, native_decision_for_tool_call


def test_native_decision_is_always_none():
    for tool in ["azure.storage.read", "azure.keyvault.get_secret", "azure.vm.start", "crm.delete_account"]:
        d = native_decision_for_tool_call(tool, "ops-agent")
        assert d["native_decision"] is None
        assert "No Azure native" in d["native_reason"]


def test_location_rule():
    assert evaluate("azure_policy_location", {"region": "germanywestcentral"})["decision"] == "allow"
    assert evaluate("azure_policy_location", {"region": "eastus"})["decision"] == "deny"


def test_storage_and_encryption():
    assert evaluate("storage_public", {"public_blob": True, "resource_id": "x"})["decision"] == "deny"
    assert evaluate("storage_public", {"public_blob": False})["decision"] == "allow"
    assert evaluate("encryption", {"encryption": False, "resource_id": "x"})["decision"] == "deny"
    assert evaluate("encryption", {"encryption": True, "tls_min": "1.0"})["decision"] == "deny"
    assert evaluate("encryption", {"encryption": True, "tls_min": "1.2"})["decision"] == "allow"


def test_mfa_and_keyvault():
    assert evaluate("mfa", {"mfa_enabled": False, "user": "x"})["decision"] == "deny"
    assert evaluate("mfa", {"mfa_enabled": True, "ca_compliant": False, "user": "x"})["decision"] == "needs_approval"
    assert evaluate("keyvault_expiry", {"secrets_expired": 2, "resource_id": "kv"})["decision"] == "deny"
    assert evaluate("keyvault_expiry", {"secrets_expired": 0, "purge_protection": True, "rbac": True})["decision"] == "allow"


def test_ai_content_filter():
    assert evaluate("ai_content_filter", {"content_filter": False, "resource_id": "aoai-test"})["decision"] == "deny"
    assert evaluate("ai_content_filter", {"content_filter": True, "jailbreak_filter": True, "logging": True})["decision"] == "allow"


def test_gateway_tool_call():
    base = {"agent_id": "ops-agent", "tool": "azure.storage.read", "agent_status": "active", "eu_tier": "minimal", "tool_pinned": True}
    r = evaluate("gateway_tool_call", base)
    assert r["decision"] == "allow" and r["native_decision"] is None
    r = evaluate("gateway_tool_call", {**base, "tool": "azure.vm.start"})
    assert r["decision"] == "needs_approval"
    r = evaluate("gateway_tool_call", {**base, "tool": "crm.delete_account"})
    assert r["decision"] == "deny"
    r = evaluate("gateway_tool_call", {**base, "agent_status": "blocked"})
    assert r["decision"] == "deny"
    r = evaluate("gateway_tool_call", {**base, "eu_tier": "prohibited"})
    assert r["decision"] == "deny"
    r = evaluate("gateway_tool_call", {**base, "tool_pinned": False})
    assert r["decision"] == "deny"


def test_unknown_rule_denies():
    assert evaluate("no_such_rule", {})["decision"] == "deny"


def test_classify():
    assert classify_use_case("Score customers across unrelated data", "", True)["tier"] == "prohibited"
    assert classify_use_case("Screen job applicants", "", True)["tier"] == "high-risk"
    assert classify_use_case("Internal chatbot for FAQs", "personal data", False)["tier"] == "limited"
    assert classify_use_case("Summarise public docs", "", False)["tier"] == "minimal"
