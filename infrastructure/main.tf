# main.tf
resource "random_id" "env_suffix" {
  byte_length = 4
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
  name    = "allow-lb-traffic"
  network = google_compute_network.custom_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"] # GCP health check ranges
}

#---------------------Cloud Run Service----------------------
resource "google_cloud_run_service" "container_service" {
  name     = "app-${var.region}-${random_id.env_suffix.hex}"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/vehicle-insurance-app:latest"
        ports {
          container_port = 5000
        }

        resources {
          limits = {
            cpu    = "1000m"  # 1 vCPU
            memory = "512Mi"  # 512MB RAM
          }
        }
      }

      # Auto-scaling limits
      scaling {
        min_instance_count = 1  # At least 1 instance always running
        max_instance_count = 10 # Scale up to 10 instances max
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
  name                  = "cloud-run-neg"
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
    "roles/run.admin"
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${var.service_account_email}"
}

#---------------------Cloud Logging----------------------
resource "google_logging_project_sink" "app_logs" {
  name        = "app-logs"
  destination = "logging.googleapis.com/projects/${var.project_id}/locations/global/buckets/_Default"
}

#---------------------Artifact Registry----------------------
resource "google_artifact_registry_repository" "my_repo" {
  location      = var.region
  repository_id = "my-app"
  format        = "DOCKER"
}

#---------------------Auto Scaling----------------------
