variable "name" { type = string }
variable "alert_email" { type = string }
variable "instance_id" { type = string }
variable "alb_arn_suffix" { type = string }
variable "target_group_arn_suffix" { type = string }
variable "db_instance_id" { type = string }

variable "cpu_threshold" {
  type    = number
  default = 80
}

variable "http_5xx_rate_threshold" {
  type    = number
  default = 5
}

variable "min_requests_for_5xx_alarm" {
  description = "Ignore the 5xx % when traffic is tiny (1 error in 2 requests = 50%)."
  type        = number
  default     = 10
}
