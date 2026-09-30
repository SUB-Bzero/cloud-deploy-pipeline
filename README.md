# Automated Cloud Deployment Pipeline (AWS · Terraform · GitHub Actions)

A containerised Flask + PostgreSQL app deployed to AWS with Infrastructure-as-Code,
a 4-stage CI/CD pipeline, health checks, CloudWatch e-mail alerts and automatic rollback.

```
Internet ─► Application Load Balancer ─► EC2 (Docker: Flask/gunicorn) ─► RDS PostgreSQL (private)
                       ▲                                  ▲
            GitHub Actions ─► ECR (image) ─► SSM deploy ──┘      CloudWatch ─► SNS ─► e-mail
```

| Path | Purpose |
|---|---|
| `app/` | Flask app (`/`, `/health`, `/api/notes`), unit tests, **multi-stage Dockerfile** |
| `docker-compose.yml` | Local web + PostgreSQL stack |
| `terraform/bootstrap/` | One-time: S3 state bucket, DynamoDB lock table, ECR repo |
| `terraform/` + `modules/` | `vpc`, `database` (RDS), `compute` (EC2 + ALB + IAM), `monitoring` (CloudWatch + SNS) |
| `.github/workflows/deploy.yml` | test → build/push → terraform apply → deploy (+ smoke test) |
| `scripts/deploy.sh` | Runs on EC2 via SSM: start new container, health-check, **auto-rollback** |
| `docs/` | Report assets, evidence, image generator |

## 1. Run locally
```bash
docker compose up --build
curl http://localhost:8000/health          # {"database":"up","status":"ok",...}
curl -X POST localhost:8000/api/notes -H 'content-type: application/json' -d '{"text":"hello"}'
curl http://localhost:8000/api/notes
# tests
cd app && pip install -r requirements-dev.txt && flake8 && pytest -v
```

## 2. One-time AWS setup
```bash
# 2a. credentials: an IAM user/role with rights for EC2, ELB, RDS, VPC, IAM, S3, DynamoDB, ECR, SSM, CloudWatch, SNS
aws configure

# 2b. bootstrap remote state + ECR
cd terraform/bootstrap
terraform init && terraform apply
terraform output            # note: state_bucket, lock_table, ecr_repository_name
```

## 3. GitHub configuration (Settings → Secrets and variables → Actions)
| Type | Name | Value |
|---|---|---|
| Secret | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | pipeline IAM credentials |
| Secret | `TF_STATE_BUCKET` | output `state_bucket` |
| Secret | `TF_LOCK_TABLE` | output `lock_table` |
| Secret | `ALERT_EMAIL` | address that receives alarm e-mails |
| Variable | `AWS_REGION` | e.g. `af-south-1` (same as bootstrap) |
| Variable | `ECR_REPOSITORY` | `capstone-app` (output `ecr_repository_name`) |
| Variable | `ENABLE_FAULT_ENDPOINT` | `true` only for the 5xx alarm demo, otherwise `false` |

Then `git push origin main` – the pipeline does the rest. Open the URL from the
`terraform apply` output (`app_url`) and **confirm the SNS subscription e-mail** once.

## 4. Demonstrate monitoring & rollback
* **5xx alarm** – set `ENABLE_FAULT_ENDPOINT=true`, redeploy, then
  `for i in $(seq 1 40); do curl -s -o /dev/null http://<alb-dns>/boom; done` → alarm `…-http-5xx-rate` → e-mail.
* **CPU alarm** – SSM Session Manager into the host and run `yes > /dev/null &` (×2) for ~10 min.
* **Rollback** – push a commit that breaks the app start-up (e.g. raise in `app.py`); the deploy job
  shows `FAILED health check → ROLLING BACK`, the previous image keeps serving traffic, and the job fails.
  Terraform state itself is versioned in S3 (restore an earlier object version to undo an infra change).

## 5. Tear down (avoid charges)
```bash
cd terraform && terraform init -backend-config=... && terraform destroy -var alert_email=you@example.com
cd bootstrap && terraform destroy     # state bucket has prevent_destroy: remove that block first
```
Estimated cost while running: EC2 t3.micro + ALB + RDS db.t3.micro ≈ US$40-50/month – destroy when done.
