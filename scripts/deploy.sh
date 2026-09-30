#!/bin/bash
# Runs ON the EC2 host (sent by GitHub Actions through AWS SSM Run Command).
# Usage: deploy.sh <full-image-uri> [enable_fault_endpoint]
#
# Flow:  pull new image -> stop old container -> start new one -> poll /health
#        healthy  -> keep new version, remember it as "last good"
#        unhealthy-> AUTOMATIC ROLLBACK to the previous image, exit 1 (pipeline fails)
set -uo pipefail

IMAGE="${1:?image uri required}"
FAULT="${2:-false}"
APP=capstone-app
APP_DIR="${APP_DIR:-/opt/app}"
STATE="$APP_DIR/last_good_image"
source "$APP_DIR/host.env"          # AWS_REGION, DB_PARAM

REGISTRY="${IMAGE%%/*}"
PREVIOUS="$(cat "$STATE" 2>/dev/null || true)"

echo ">> Logging in to ECR ($REGISTRY)"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY" || exit 1

echo ">> Pulling $IMAGE"
docker pull "$IMAGE" || exit 1

DATABASE_URL="$(aws ssm get-parameter --name "$DB_PARAM" --with-decryption \
  --region "$AWS_REGION" --query Parameter.Value --output text)" || exit 1

start_container() {   # $1 = image
  docker rm -f "$APP" >/dev/null 2>&1 || true
  docker run -d --name "$APP" --restart unless-stopped -p 80:8000 \
    -e DATABASE_URL="$DATABASE_URL" \
    -e ENABLE_FAULT_ENDPOINT="$FAULT" \
    "$1" >/dev/null
}

healthy() {           # poll /health for up to ~60 s
  for i in $(seq 1 20); do
    if curl -fsS -m 3 http://127.0.0.1/health >/dev/null 2>&1; then
      return 0
    fi
    sleep "${POLL_SLEEP:-3}"
  done
  return 1
}

echo ">> Starting new version"
start_container "$IMAGE"

if healthy; then
  echo "$IMAGE" > "$STATE"
  echo ">> SUCCESS: $IMAGE is healthy"
  docker image prune -f >/dev/null 2>&1 || true
  exit 0
fi

echo "!! New version FAILED health check"
docker logs --tail 40 "$APP" || true

if [ -n "$PREVIOUS" ]; then
  echo ">> ROLLING BACK to $PREVIOUS"
  start_container "$PREVIOUS"
  if healthy; then
    echo ">> Rollback complete - previous version is serving traffic"
  else
    echo "!! Rollback version is also unhealthy - manual action required"
  fi
else
  echo "!! No previous version to roll back to (first deployment)"
fi
exit 1
