variable "region" {
  default = "us-east-1"
}

variable "env" {
  default = "dev"
}

variable "tag" {}

variable "app_name" {
  default = "open-library"
}


variable "cloudwatch_access" {
  default = "Allow"
}

#lambda
variable "lambda_memory_size" {
  default = "1024"
}

variable "lambda_timeout" {
  default = "900"
}

#event-bridge
variable "event_bridge_rule_name" {
  default = "open-library"
}

variable "event_bridge_schedule_expression" {
  default = "rate(1 day)"
}
