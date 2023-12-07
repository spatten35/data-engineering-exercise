provider "aws" {
  region  = var.region
}

terraform {
  backend "s3" {
    key    = "open-library-dummy-bucket/open-library"
    region = "us-east-1"
  }
}

data "aws_caller_identity" "current" {}