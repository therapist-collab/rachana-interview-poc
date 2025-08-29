########################################
# Networking placeholders (org-level)
# VPC-SC perimeters + Private Google Access often require org admin.
# Document intent here; do not fail apply if you lack permissions.
########################################


# - VPC-SC perimeter: google_access_context_manager_service_perimeter
# - Private Google Access: add to subnetwork


# resource "google_access_context_manager_access_policy" "org" { ... }
# resource "google_access_context_manager_service_perimeter" "poc" { ... }

# resource "google_compute_network" "vpc" { name = "poc-vpc" auto_create_subnetworks = false }
# resource "google_compute_subnetwork" "subnet" {
#   name                  = "poc-subnet"
#   ip_cidr_range         = "10.10.0.0/24"
#   region                = var.region
#   network               = google_compute_network.vpc.id
#   private_ip_google_access = true   # <-- Private Google Access
# }
