variable "domain" {
  description = "The domain name for ai_jam."
  type        = string
}

variable "env" {
  description = "Environment name (e.g. prod, staging)."
  type        = string
}

variable "region" {
  description = "AWS region."
  type        = string
  default     = "ca-central-1"
}

variable "account_id" {
  description = "AWS account ID."
  type        = string
}

variable "billing_code" {
  description = "Billing code tag value."
  type        = string
}

variable "product_name" {
  description = "(Required) The name of the product you are deploying."
  type        = string
}