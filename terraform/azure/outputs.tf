output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "acr_login_server" {
  description = "Container registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "postgresql_fqdn" {
  description = "PostgreSQL FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
  sensitive   = true
}

output "redis_hostname" {
  description = "Redis hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}
