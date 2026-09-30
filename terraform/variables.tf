variable "aws_region" {
  type    = string
  default = "af-south-1"
}

variable "project" {
  type    = string
  default = "capstone-app"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "alert_email" {
  description = "Address that receives CloudWatch alarm e-mails (must confirm the SNS subscription)."
  type        = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "cpu_alarm_threshold" {
  type    = number
  default = 80
}

variable "http_5xx_rate_threshold" {
  description = "Alarm when 5xx responses exceed this percentage of requests."
  type        = number
  default     = 5
}
