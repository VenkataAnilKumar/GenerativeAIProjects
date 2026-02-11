output "vpc_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "artifact_registry" {
  description = "Artifact Registry repository"
  value       = google_artifact_registry_repository.main.name
}

output "cloud_sql_instance" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "redis_host" {
  description = "Redis host"
  value       = google_redis_instance.main.host
}

output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "storage_bucket" {
  description = "Storage bucket name"
  value       = google_storage_bucket.artifacts.name
}
