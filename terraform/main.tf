resource "aws_ecr_repository" "mock_notify_service" {
  name                 = "mock-notify-service"
  image_scanning_configuration {
    scan_on_push = false
  }
}

module "mock_notify_service" {
  source    = "github.com/cds-snc/terraform-modules//lambda?ref=v10.5.1"
  name      = "mock-notify-service-api"
  ecr_arn   = aws_ecr_repository.mock_notify_service.arn
  image_uri = "${aws_ecr_repository.mock_notify_service.repository_url}:latest"

  memory                 = 1024
  timeout                = 30
  enable_lambda_insights = false
  architectures          = ["arm64"]

  environment_variables = {
    GITHUB_PUBLIC_KEYS_URL = "your-secret-session-key-here"
  }

  billing_tag_value = "mock-notify-service"
}

resource "aws_lambda_function_url" "mock_notify_service" {
  function_name      = module.mock_notify_service.function_name
  authorization_type = "NONE"
}
