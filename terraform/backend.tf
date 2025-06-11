terraform {
  backend "s3" {
    bucket        = "ai-jam-session-mock-service-tf"
    key           = "terraform/state/terraform.tfstate"
    region        = "ca-central-1"
    use_lockfile  = true
  }
}