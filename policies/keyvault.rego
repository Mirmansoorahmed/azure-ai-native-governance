package azure_native.keyvault

# keyvault: one decision, allow / deny.
default decision := "deny"
default reason := "Key Vault has expired secrets"

decision := "allow" if {
    input.secrets_expired == 0
}

reason := "No expired secrets" if {
    input.secrets_expired == 0
} else := "Key Vault has expired secrets"
