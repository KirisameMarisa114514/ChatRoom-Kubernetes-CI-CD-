#!/bin/bash
set -e

TAG=${1:-$(date +%Y%m%d%H%M%S)}
REGISTRY="192.168.30.10:5000"

BACKEND_IMAGE="$REGISTRY/chat-backend:$TAG"
FRONTEND_IMAGE="$REGISTRY/chat-frontend:$TAG"

echo "[1/7] Build backend image..."
docker build -t "$BACKEND_IMAGE" ./backend

echo "[2/7] Build frontend image..."
docker build -t "$FRONTEND_IMAGE" ./frontend

echo "[3/7] Push backend image..."
docker push "$BACKEND_IMAGE"

echo "[4/7] Push frontend image..."
docker push "$FRONTEND_IMAGE"

echo "[5/7] Update backend deployment..."
kubectl set image deployment/chat-backend chat-backend="$BACKEND_IMAGE"

echo "[6/7] Update frontend deployment..."
kubectl set image deployment/chat-frontend chat-frontend="$FRONTEND_IMAGE"

echo "[7/7] Wait rollout..."
kubectl rollout status deployment/chat-backend
kubectl rollout status deployment/chat-frontend

echo "Deploy success."
echo "Backend image:  $BACKEND_IMAGE"
echo "Frontend image: $FRONTEND_IMAGE"
echo "Visit: http://192.168.30.10:30080"

echo "[cleanup] Remove stuck terminating pods if any..."
for p in $(kubectl get pods | awk '/Terminating/ {print $1}'); do
  kubectl delete pod "$p" --grace-period=0 --force --wait=false || true
done