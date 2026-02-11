variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "genai-platform"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
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

variable "db_tier" {
  description = "Cloud SQL tier"
  type        = string
  default     = "db-f1-micro"
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
