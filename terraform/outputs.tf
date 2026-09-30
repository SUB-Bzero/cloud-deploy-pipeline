output "app_url" {
  value = "http://${module.compute.alb_dns_name}"
}

output "health_url" {
  value = "http://${module.compute.alb_dns_name}/health"
}

output "instance_id" {
  value = module.compute.instance_id
}

output "rds_endpoint" {
  value = module.database.db_endpoint
}

output "sns_topic_arn" {
  value = module.monitoring.sns_topic_arn
}
