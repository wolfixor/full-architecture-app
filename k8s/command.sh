kubectl apply -f postgres.yaml

kubectl apply -f migration-job.yaml

kubectl wait \
  --for=condition=complete \
  job/task-api-migration \
  -n task-api \
  --timeout=300s

kubectl apply -f task-api.yaml