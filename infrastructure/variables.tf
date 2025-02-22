# variables.tf
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
  description = "Path to GCP Service Account Credentials JSON file"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for Terraform operations"
  type        = string
}

