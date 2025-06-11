resource "aws_lb" "ai_jam" {
  name               = "ai-jam-${var.env}"
  internal           = false
  load_balancer_type = "application"

  drop_invalid_header_fields = true
  enable_deletion_protection = true

  security_groups = [
    aws_security_group.ai_jam_lb.id
  ]
  subnets = module.vpc.public_subnet_ids

  tags = local.common_tags
}

resource "random_string" "alb_tg_suffix" {
  length  = 3
  special = false
  upper   = false
}

resource "aws_lb_target_group" "ai_jam" {
  name                 = "ai-jam-tg-${random_string.alb_tg_suffix.result}"
  port                 = 8080
  protocol             = "HTTP"
  target_type          = "ip"
  deregistration_delay = 30
  vpc_id               = module.vpc.vpc_id

  health_check {
    enabled  = true
    protocol = "HTTP"
    path     = "/"
    matcher  = "200-399"
  }

  stickiness {
    type = "lb_cookie"
  }

  tags = local.common_tags

  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      stickiness[0].cookie_name
    ]
  }
}

resource "aws_lb_target_group" "ai_jam_forms" {
  name                 = "ai-jam-forms-tg-${random_string.alb_tg_suffix.result}"
  port                 = 8081
  protocol             = "HTTP"
  target_type          = "ip"
  deregistration_delay = 30
  vpc_id               = module.vpc.vpc_id

  health_check {
    enabled  = true
    protocol = "HTTP"
    path     = "/"
    matcher  = "200-399"
  }

  stickiness {
    type = "lb_cookie"
  }

  tags = local.common_tags

  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      stickiness[0].cookie_name
    ]
  }
}

resource "aws_lb_listener" "ai_jam" {
  load_balancer_arn = aws_lb.ai_jam.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-3-FIPS-2023-04"
  certificate_arn   = aws_acm_certificate.ai_jam.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ai_jam.arn
  }

  depends_on = [
    aws_acm_certificate_validation.ai_jam,
    aws_route53_record.ai_jam_validation,
  ]

  tags = local.common_tags
}

resource "aws_alb_listener_rule" "ai_jam" {
  listener_arn = aws_lb_listener.ai_jam.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ai_jam_forms.arn
  }

  condition {
    host_header {
      values = ["forms.${var.domain}"]
    }
  }
}
