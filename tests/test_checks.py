from app.checks import run_all_checks


def test_16_checks():
    checks = run_all_checks()
    assert len(checks) == 16
    codes = [c["control_code"] for c in checks]
    assert len(set(codes)) == 16


def test_public_storage_fails():
    checks = {c["test_name"]: c for c in run_all_checks()}
    assert checks["storage_public_blob_deny"]["result"] == "Fail"
    assert "stnordlichtpub" in checks["storage_public_blob_deny"]["details"]["public_accounts"]


def test_allowed_locations_fails():
    checks = {c["test_name"]: c for c in run_all_checks()}
    assert checks["azure_policy_allowed_locations"]["result"] == "Fail"
    assert "rg-test" in checks["azure_policy_allowed_locations"]["details"]["regions_outside_allowed"]


def test_ai_filters_and_residency_fail():
    checks = {c["test_name"]: c for c in run_all_checks()}
    assert checks["azure_openai_content_filters"]["result"] == "Fail"
    assert checks["ai_data_residency_eu"]["result"] == "Fail"
    assert "aoai-test" in checks["azure_openai_content_filters"]["details"]["unfiltered"]


def test_gap_check_is_partial_by_design():
    checks = {c["test_name"]: c for c in run_all_checks()}
    gap = checks["per_tool_call_decision_gap"]
    assert gap["result"] == "Partial"
    assert gap["details"]["native_decision"] is None
    assert "OPA" in gap["details"]["gateway_decision"]


def test_defender_score_partial():
    checks = {c["test_name"]: c for c in run_all_checks()}
    assert checks["defender_secure_score"]["result"] == "Partial"
    assert checks["defender_secure_score"]["details"]["secure_score_pct"] == 62
