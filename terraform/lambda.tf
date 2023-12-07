resource "aws_iam_role" "open_library_iam_role" {
  name = "${var.app_name}-${var.env}-role"
  assume_role_policy = file("${path.module}/lambda-role.json")
}

resource "aws_iam_role_policy" "open_library_iam_policy" {
  name = "${var.app_name}-${var.env}-policy"
  role = aws_iam_role.open_library_iam_role.id
  policy = templatefile("${path.module}/lambda-policy.json", {
    env               = var.env
    cloudwatch_access = var.cloudwatch_access
    region            = var.region
    account_id        = data.aws_caller_identity.current.account_id
  })
}

resource "aws_lambda_function" "open_library" {
  function_name                  = "${var.app_name}-${var.env}"
  role                           = aws_iam_role.open_library_iam_role.arn
  package_type                   = "Image"
  timeout                        = var.lambda_timeout
  publish                        = true
  memory_size                    = var.lambda_memory_size
  reserved_concurrent_executions = var.env == "prod" ? 100 : -1
}

resource "aws_lambda_alias" "live" {
  name             = "live"
  function_name    = aws_lambda_function.open_library.arn
  function_version = aws_lambda_function.open_library.version

  lifecycle {
    ignore_changes = [function_version]
  }
}

resource "aws_lambda_permission" "allow_event_bridge" {
  count         = (var.env == "prod") ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.open_library.function_name
  principal     = "events.amazonaws.com"
  source_arn    = module.eventbridge.eventbridge_rule_arns["${var.event_bridge_rule_name}-${var.env}"]
  qualifier     = aws_lambda_alias.live.name
}
