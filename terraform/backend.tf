# Remote state in S3 (created by ./bootstrap). Bucket/region/table are injected at
# init time so the same code works in any account:
#   terraform init -backend-config="bucket=<state-bucket>" \
#                  -backend-config="region=<region>" \
#                  -backend-config="dynamodb_table=<lock-table>"
terraform {
  backend "s3" {
    key     = "capstone/terraform.tfstate"
    encrypt = true
  }
}
