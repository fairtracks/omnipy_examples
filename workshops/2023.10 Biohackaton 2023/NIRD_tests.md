# Prefect tests

1. Deploy the server usign ``helm install prefect-server-test ./charts/prefect-server/ --namespace fairtracks-ns10022k`` and verify that the pod is running with 
``kubectl get pods -n fairtracks-ns10022k`` and that the
ingress is working with ``kubectl -n fairtracks-ns10022k get ingress``
2. Create a kubernetes workpool, you can use the name "kubernetes-agent" as it is the same configure in 
the worker.  
3. Deploy the worker ``helm install prefect-worker-test ./charts/prefect-worker/ --namespace fairtracks-ns10022k``
3. Export the api url  ``export PREFECT_API_URL=http://prefect.fairtracks.sigma2.no/api``
4. Optional? Setup ``prefect config set PREFECT_API_URL=http://prefect.fairtracks.sigma2.no/api``
5.  Run a deployment ``prefect deploy``, select "Enter a flow entrypoint manually"