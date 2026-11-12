package azure_native.content_filter

# content_filter: one decision, allow / deny.
default decision := "deny"
default reason := "AI resource has no content filter"

decision := "allow" if {
    input.content_filter == true
}

reason := "Content filter on" if {
    input.content_filter == true
} else := "AI resource has no content filter"
