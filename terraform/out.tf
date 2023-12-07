output "lambda_api_version" {
  value = aws_lambda_function.open_library.version
}

output "lambda_api_arn" {
  value = aws_lambda_function.open_library.arn
}