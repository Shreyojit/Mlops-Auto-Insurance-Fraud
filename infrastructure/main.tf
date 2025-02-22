resource "random_id" "env_suffix" {
  byte_length = 4
}

#---------------------Secret Manager Configuration----------------------
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password-${random_id.env_suffix.hex}"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "mongodb_url" {
  secret_id = "mongodb-url-${random_id.env_suffix.hex}"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password
}

resource "google_secret_manager_secret_version" "mongodb_url_version" {
  secret      = google_secret_manager_secret.mongodb_url.id
  secret_data = var.mongodb_url
}

#---------------------VPC Network----------------------
resource "google_compute_network" "custom_vpc" {
  name                    = "main-vpc-${var.region}-${random_id.env_suffix.hex}"
  auto_create_subnetworks = false
}

#---------------------Public Subnets----------------------
resource "google_compute_subnetwork" "public_subnet1" {
  name          = "subnet1-${var.region}-${random_id.env_suffix.hex}"
  ip_cidr_range = "10.1.0.0/18"
  region        = var.region
  network       = google_compute_network.custom_vpc.id
}

resource "google_compute_subnetwork" "public_subnet2" {
  name          = "subnet2-${var.region}-${random_id.env_suffix.hex}"
  ip_cidr_range = "10.1.64.0/18"
  region        = var.region
  network       = google_compute_network.custom_vpc.id
}

#---------------------Firewall Rules----------------------
resource "google_compute_firewall" "allow_lb" {
  name    = "allow-lb-traffic-${random_id.env_suffix.hex}"
  network = google_compute_network.custom_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
}

#---------------------Cloud Run Service----------------------
resource "google_cloud_run_service" "container_service" {
  name     = "app-${var.region}-${random_id.env_suffix.hex}"
  location = var.region

  template {
    spec {
      service_account_name = var.service_account_email
      containers {
        image = "gcr.io/${var.project_id}/vehicle-insurance-app:latest"
        ports {
          container_port = 5000
        }
        env {
          name = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_password.secret_id
              key  = "latest"
            }
          }
        }
        env {
          name = "MONGODB_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.mongodb_url.secret_id
              key  = "latest"
            }
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

#---------------------Load Balancer Components----------------------
resource "google_compute_global_address" "lb_ip" {
  name = "lb-ip-${var.region}-${random_id.env_suffix.hex}"
}

resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  name                  = "cloud-run-neg-${random_id.env_suffix.hex}"
  region                = var.region
  network_endpoint_type = "SERVERLESS"
  cloud_run {
    service = google_cloud_run_service.container_service.name
  }
}

resource "google_compute_backend_service" "backend" {
  name        = "backend-service-${random_id.env_suffix.hex}"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 30

  backend {
    group = google_compute_region_network_endpoint_group.serverless_neg.id
  }
}

resource "google_compute_url_map" "default" {
  name            = "lb-urlmap-${random_id.env_suffix.hex}"
  default_service = google_compute_backend_service.backend.id
}

resource "google_compute_target_http_proxy" "default" {
  name    = "http-proxy-${random_id.env_suffix.hex}"
  url_map = google_compute_url_map.default.id
}

resource "google_compute_global_forwarding_rule" "default" {
  name       = "forwarding-rule-${random_id.env_suffix.hex}"
  target     = google_compute_target_http_proxy.default.id
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address
}

#---------------------IAM Configuration----------------------
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.container_service.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_project_iam_member" "terraform_roles" {
  for_each = toset([
    "roles/storage.admin",
    "roles/logging.admin",
    "roles/run.admin",
    "roles/secretmanager.admin"
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${var.service_account_email}"
}

resource "google_secret_manager_secret_iam_member" "secret_access" {
  for_each = {
    db_password = google_secret_manager_secret.db_password.secret_id
    mongodb_url = google_secret_manager_secret.mongodb_url.secret_id
  }

  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.service_account_email}"
}

#---------------------Outputs----------------------
output "load_balancer_ip" {
  description = "IP Address of the Global Load Balancer"
  value       = google_compute_global_address.lb_ip.address
}

output "cloud_run_url" {
  description = "Direct URL of the Cloud Run Service"
  value       = google_cloud_run_service.container_service.status[0].url
}

output "vpc_name" {
  description = "Name of the VPC Network"
  value       = google_compute_network.custom_vpc.name
}