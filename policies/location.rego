package azure_native.location

# location: one decision, allow / deny.
default decision := "deny"
default reason := "Region is outside the allowed EU regions"

decision := "allow" if {
    input.region == "germanywestcentral" or input.region == "westeurope"
}

reason := "Region is allowed" if {
    input.region == "germanywestcentral" or input.region == "westeurope"
} else := "Region is outside the allowed EU regions"
