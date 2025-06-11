locals {
  common_tags = {
    Terraform  = "true"
    CostCentre = var.billing_code
  }
}

module "vpc" {
  source = "github.com/cds-snc/terraform-modules//vpc?ref=v10.4.6"
  name   = "ai-jam-${var.env}"

  enable_flow_log                  = true
  availability_zones               = 2
  cidrsubnet_newbits               = 8
  single_nat_gateway               = true
  allow_https_request_out          = true
  allow_https_request_out_response = true
  allow_https_request_in           = true
  allow_https_request_in_response  = true

  billing_tag_value = var.billing_code
}

#
# Security groups
#

# ECS
resource "aws_security_group" "ai_jam_ecs" {
  description = "NSG for ai_jam ECS Tasks"
  name        = "ai_jam_ecs"
  vpc_id      = module.vpc.vpc_id
  tags        = local.common_tags
}

resource "aws_security_group_rule" "ai_jam_ecs_egress_all" {
  type              = "egress"
  protocol          = "-1"
  to_port           = 0
  from_port         = 0
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ai_jam_ecs.id
}

resource "aws_security_group_rule" "ai_jam_ecs_ingress_lb" {
  description              = "Ingress from load balancer to ai_jam ECS task"
  type                     = "ingress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ai_jam_ecs.id
  source_security_group_id = aws_security_group.ai_jam_lb.id
}

resource "aws_security_group_rule" "ai_jam_ecs_ingress_forms_lb" {
  description              = "Ingress from load balancer to ai_jam Forms ECS task"
  type                     = "ingress"
  from_port                = 8081
  to_port                  = 8081
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ai_jam_ecs.id
  source_security_group_id = aws_security_group.ai_jam_lb.id
}

# Load balancer
resource "aws_security_group" "ai_jam_lb" {
  name        = "ai_jam_lb"
  description = "NSG for ai_jam load balancer"
  vpc_id      = module.vpc.vpc_id
  tags        = local.common_tags
}

resource "aws_security_group_rule" "ai_jam_lb_ingress_internet_https" {
  description       = "Ingress from internet to load balancer (HTTPS)"
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.ai_jam_lb.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "ai_jam_lb_egress_ecs" {
  description              = "Egress from load balancer to ai_jam ECS task"
  type                     = "egress"
  from_port                = 8080
  to_port                  = 8080
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ai_jam_lb.id
  source_security_group_id = aws_security_group.ai_jam_ecs.id
}

resource "aws_security_group_rule" "ai_jam_lb_egress_forms_ecs" {
  description              = "Egress from load balancer to ai_jam Forms ECS task"
  type                     = "egress"
  from_port                = 8081
  to_port                  = 8081
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ai_jam_lb.id
  source_security_group_id = aws_security_group.ai_jam_ecs.id
}