variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Deployment Region"
  type        = string
  default     = "asia-south1"
}

variable "credentials_file" {
  description = "../credentials.json"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for Terraform operations"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "mongodb_url" {
  description = "MongoDB connection URL"
  type        = string
  sensitive   = true
}