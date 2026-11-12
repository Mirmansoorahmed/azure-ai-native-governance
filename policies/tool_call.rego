package azure_native.tool_call

# Gateway tool call: deny by default. Native applications make NO
# decision here — native_decision is always null; the gateway decides.
default decision := "deny"
default reason := "Tool is not allowlisted for this agent"

decision := "allow" if {
    input.tool_pinned != false
    input.agent_status != "blocked"
    input.eu_tier != "prohibited"
    input.tool == input.allowlisted_tool
}

decision := "needs_approval" if {
    input.tool_pinned != false
    input.agent_status != "blocked"
    input.eu_tier != "prohibited"
    input.tool in ["azure.vm.start", "azure.vm.stop", "azure.keyvault.get_secret", "crm.send_email", "hr.rank_applicant"]
}

reason := "Tool is allowlisted for this agent" if {
    decision == "allow"
} else := "Tool always requires human approval" if {
    decision == "needs_approval"
} else := "Tool is not allowlisted for this agent"
