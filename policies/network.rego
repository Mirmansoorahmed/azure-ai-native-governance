package azure_native.network

# network: one decision, allow / deny.
default decision := "deny"
default reason := "No private endpoint"

decision := "allow" if {
    input.private_endpoint == true
}

reason := "Private endpoint in place" if {
    input.private_endpoint == true
} else := "No private endpoint"
