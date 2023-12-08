##################
# EventBridge
##################
module "eventbridge" {
  create = (var.env == "prod")
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "1.17.3"

  create_bus = false

  rules = {
    "${var.event_bridge_rule_name}-${var.env}" = {
      description         = "Trigger open-library-${var.env} Lambda"
      schedule_expression = var.event_bridge_schedule_expression
    }
  }

  targets = {
    "${var.event_bridge_rule_name}-${var.env}" = [
      {
        name  = "open-library-${var.env}-cron"
        arn   = aws_lambda_alias.live.arn
        input = jsonencode({ "job" : "cron-by-rate" })
      }
    ]
  }

}