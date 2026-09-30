output "state_bucket" { value = aws_s3_bucket.tfstate.id }
output "lock_table" { value = aws_dynamodb_table.tflock.name }
output "ecr_repository_url" { value = aws_ecr_repository.app.repository_url }
output "ecr_repository_name" { value = aws_ecr_repository.app.name }
