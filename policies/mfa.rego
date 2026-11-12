package azure_native.mfa

# mfa: one decision, allow / deny.
default decision := "deny"
default reason := "User has no MFA"

decision := "allow" if {
    input.mfa_enabled == true
}

reason := "MFA enabled" if {
    input.mfa_enabled == true
} else := "User has no MFA"
