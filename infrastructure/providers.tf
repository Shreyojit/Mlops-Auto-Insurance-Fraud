terraform {
  backend "gcs" {
    bucket      = "churn-cloud-project-446615-tfstate"
    prefix      = "terraform/state"
    credentials = "credentials.json"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials_file)
}