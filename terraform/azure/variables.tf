variable "project_name" {
  description = "Project name"
  type        = string
  default     = "genai-platform"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
}

variable "vnet_cidr" {
  description = "VNet CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "app_subnet_cidr" {
  description = "Application subnet CIDR"
  type        = string
  default     = "10.0.1.0/24"
}

variable "db_subnet_cidr" {
  description = "Database subnet CIDR"
  type        = string
  default     = "10.0.2.0/24"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "genai_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_sku_name" {
  description = "PostgreSQL SKU"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {
    Project     = "GenAI Platform"
    ManagedBy   = "Terraform"
  }
}
