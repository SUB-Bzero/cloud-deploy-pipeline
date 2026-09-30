output "db_endpoint" { value = aws_db_instance.this.endpoint }
output "db_instance_id" { value = aws_db_instance.this.identifier }
output "db_url_parameter_name" { value = aws_ssm_parameter.database_url.name }
output "db_url_parameter_arn" { value = aws_ssm_parameter.database_url.arn }
