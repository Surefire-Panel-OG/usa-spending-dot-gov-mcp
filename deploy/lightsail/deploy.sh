#!/usr/bin/env bash
#
# Deploy the USAspending MCP server to AWS Lightsail Containers.
#
# Prerequisites (install once):
#   - Docker (running)                 https://docs.docker.com/get-docker/
#   - AWS CLI v2, configured (aws configure)
#   - lightsailctl plugin              https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-install-software
#   - jq
#
# Usage:
#   ./deploy/lightsail/deploy.sh            # build, push, and (re)deploy
#
set -euo pipefail

SERVICE_NAME="usaspending-mcp"
POWER="micro"          # nano|micro|small|... ($7/mo micro is plenty here)
SCALE="1"              # number of container nodes
AWS_REGION="${AWS_REGION:-us-east-1}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_CONTEXT="${REPO_ROOT}/usaspending-mcp-server"
SPEC="${REPO_ROOT}/deploy/lightsail/containers.json"

echo "==> Region: ${AWS_REGION} | Service: ${SERVICE_NAME}"

# 1. Create the container service if it does not already exist.
if ! aws lightsail get-container-services --service-name "${SERVICE_NAME}" \
      --region "${AWS_REGION}" >/dev/null 2>&1; then
  echo "==> Creating container service (${POWER}, scale ${SCALE})..."
  aws lightsail create-container-service \
    --service-name "${SERVICE_NAME}" \
    --power "${POWER}" \
    --scale "${SCALE}" \
    --region "${AWS_REGION}"
  echo "==> Waiting for service to become READY..."
  until [ "$(aws lightsail get-container-services --service-name "${SERVICE_NAME}" \
              --region "${AWS_REGION}" --query 'containerServices[0].state' --output text)" = "READY" ]; do
    sleep 10; echo "    ...still provisioning"
  done
else
  echo "==> Container service already exists; reusing."
fi

# 2. Build the image (linux/amd64 for Lightsail).
echo "==> Building image..."
docker build --platform linux/amd64 -t "${SERVICE_NAME}:latest" "${BUILD_CONTEXT}"

# 3. Push image to Lightsail; capture the versioned image ref it returns
#    (e.g. ":usaspending-mcp.app.7").
echo "==> Pushing image to Lightsail..."
PUSH_OUTPUT="$(aws lightsail push-container-image \
  --service-name "${SERVICE_NAME}" \
  --label app \
  --image "${SERVICE_NAME}:latest" \
  --region "${AWS_REGION}" 2>&1)"
echo "${PUSH_OUTPUT}"
IMAGE_REF="$(echo "${PUSH_OUTPUT}" | grep -oE ':'"${SERVICE_NAME}"'\.app\.[0-9]+' | tail -1)"
if [ -z "${IMAGE_REF}" ]; then
  echo "ERROR: could not parse pushed image ref from output above." >&2
  exit 1
fi
echo "==> Pushed image ref: ${IMAGE_REF}"

# 4. Render the deployment spec with the concrete image ref and deploy.
TMP_SPEC="$(mktemp)"
jq --arg img "${IMAGE_REF}" '.containers.app.image = $img' "${SPEC}" > "${TMP_SPEC}"

echo "==> Creating deployment..."
aws lightsail create-container-service-deployment \
  --service-name "${SERVICE_NAME}" \
  --region "${AWS_REGION}" \
  --cli-input-json "file://${TMP_SPEC}"
rm -f "${TMP_SPEC}"

# 5. Report the public URL.
URL="$(aws lightsail get-container-services --service-name "${SERVICE_NAME}" \
        --region "${AWS_REGION}" --query 'containerServices[0].url' --output text)"
echo ""
echo "==> Deployment submitted. Public URL: ${URL}"
echo "==> MCP endpoint (Claude Desktop / ChatGPT):      ${URL}mcp"
echo "==> Health check:                                ${URL}healthz"
echo "    (First deployment takes a few minutes to go ACTIVE.)"
