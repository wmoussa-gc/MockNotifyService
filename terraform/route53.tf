resource "aws_route53_zone" "ai_jam" {
  name = var.domain
  tags = local.common_tags
}

resource "aws_route53_record" "ai_jam_notify_A" {
  zone_id = aws_route53_zone.ai_jam.zone_id
  name    = "notify.${var.domain}"
  type    = "A"

  alias {
    name                   = aws_lb.ai_jam.dns_name
    zone_id                = aws_lb.ai_jam.zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "ai_jam_forms_A" {
  zone_id = aws_route53_zone.ai_jam.zone_id
  name    = "forms.${var.domain}"
  type    = "A"

  alias {
    name                   = aws_lb.ai_jam.dns_name
    zone_id                = aws_lb.ai_jam.zone_id
    evaluate_target_health = false
  }
}
