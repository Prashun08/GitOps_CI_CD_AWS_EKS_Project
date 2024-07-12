terraform {
  required_version = ">= 0.14"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }
  backend "http" {
  }
}
provider "aws" {
  region = "us-east-1"
}
