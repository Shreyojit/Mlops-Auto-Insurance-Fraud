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
  value       = google_compute_network.custom_vpc.name  # Already contains suffix
}

output "public_subnets" {
  description = "Details of Public Subnets"
  value = [
    {
      name   = google_compute_subnetwork.public_subnet1.name  # Auto-includes suffix
      region = google_compute_subnetwork.public_subnet1.region
      cidr   = google_compute_subnetwork.public_subnet1.ip_cidr_range
    },
    {
      name   = google_compute_subnetwork.public_subnet2.name  # Auto-includes suffix
      region = google_compute_subnetwork.public_subnet2.region
      cidr   = google_compute_subnetwork.public_subnet2.ip_cidr_range
    }
  ]
}

# Add this new output for backend service
output "backend_service_name" {
  description = "Name of the backend service"
  value       = google_compute_backend_service.backend.name
}

# Keep existing outputs unchanged - they'll auto-resolve to new names