package azure_native.storage

# storage: one decision, allow / deny.
default decision := "deny"
default reason := "Storage allows public blob access"

decision := "allow" if {
    not input.public_blob
}

reason := "No public blob access" if {
    not input.public_blob
} else := "Storage allows public blob access"
