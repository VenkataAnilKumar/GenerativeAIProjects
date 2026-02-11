terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
}

# Subnets
resource "google_compute_subnetwork" "app" {
  name          = "${var.project_name}-app-subnet"
  ip_cidr_range = var.app_subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id
}

resource "google_compute_subnetwork" "db" {
  name          = "${var.project_name}-db-subnet"
  ip_cidr_range = var.db_subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id
}

# Artifact Registry
resource "google_artifact_registry_repository" "main" {
  location      = var.region
  repository_id = "${var.project_name}-repo"
  description   = "Docker repository for GenAI Platform"
  format        = "DOCKER"
}

# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "main" {
  name             = "${var.project_name}-db"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier = var.db_tier
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.main.id
    }
    
    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }
    
    maintenance_window {
      day  = 1
      hour = 0
    }
  }
  
  deletion_protection = var.environment == "production"
}

resource "google_sql_database" "main" {
  name     = "genai"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = var.db_username
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Memorystore (Redis)
resource "google_redis_instance" "main" {
  name           = "${var.project_name}-redis"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  
  authorized_network = google_compute_network.main.id
  
  redis_version = "REDIS_7_0"
}

# Cloud Storage
resource "google_storage_bucket" "artifacts" {
  name     = "${var.project_name}-artifacts-${var.project_id}"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90
    }
  }
}

# Cloud Run Service
resource "google_cloud_run_service" "api" {
  name     = "${var.project_name}-api"
  location = var.region
  
  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}/genai-platform:latest"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "10"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access (configure as needed)
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Firewall Rules
resource "google_compute_firewall" "allow_http" {
  name    = "${var.project_name}-allow-http"
  network = google_compute_network.main.name
  
  allow {
    protocol = "tcp"
    ports    = ["8000"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}
