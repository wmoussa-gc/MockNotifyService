module "mock_notify_service" {
  source = "github.com/cds-snc/terraform-modules//ecs?ref=v10.4.6"

  cluster_name     = "ai-jam"
  service_name     = "mock-notify-service"
  task_cpu         = 1024
  task_memory      = 2048
  cpu_architecture = "ARM64"

  service_use_latest_task_def = true

  # Scaling
  enable_autoscaling = false
  desired_count      = 1

  # Task definition
  container_image                     = "${aws_ecr_repository.mock_notify_service.repository_url}:latest"
  container_host_port                 = 8080
  container_port                      = 8080
  container_read_only_root_filesystem = false

  # Networking
  lb_target_group_arn = aws_lb_target_group.ai_jam.arn
  subnet_ids          = module.vpc.private_subnet_ids
  security_group_ids  = [aws_security_group.ai_jam_ecs.id]

  billing_tag_value = var.billing_code
}

module "mock_forms_service" {
  source = "github.com/cds-snc/terraform-modules//ecs?ref=v10.4.6"

  create_cluster   = false
  cluster_name     = "ai-jam"
  service_name     = "mock-forms-service"
  task_cpu         = 1024
  task_memory      = 2048
  cpu_architecture = "ARM64"

  service_use_latest_task_def = true

  # Scaling
  enable_autoscaling = false
  desired_count      = 1

  # Task definition
  container_image                     = "${aws_ecr_repository.mock_forms_service.repository_url}:latest"
  container_host_port                 = 8081
  container_port                      = 8081
  container_read_only_root_filesystem = false

  # Networking
  lb_target_group_arn = aws_lb_target_group.ai_jam_forms.arn
  subnet_ids          = module.vpc.private_subnet_ids
  security_group_ids  = [aws_security_group.ai_jam_ecs.id]

  billing_tag_value = var.billing_code
}