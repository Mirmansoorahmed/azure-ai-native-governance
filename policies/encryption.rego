package azure_native.encryption

# encryption: one decision, allow / deny.
default decision := "deny"
default reason := "Resource is not encrypted at rest"

decision := "allow" if {
    input.encryption == true
}

reason := "Encryption at rest on" if {
    input.encryption == true
} else := "Resource is not encrypted at rest"
