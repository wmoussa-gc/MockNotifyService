resource "aws_ecr_repository" "mock_notify_service" {
  name                 = "mock-notify-service"
  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "mock_forms_service" {
  name                 = "mock-forms-service"
  image_scanning_configuration {
    scan_on_push = false
  }
}