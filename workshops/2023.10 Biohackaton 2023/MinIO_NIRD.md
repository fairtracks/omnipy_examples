# Local MinIO test:
Clone the Helm Charts Repository:
```
git clone https://github.com/UNINETTSigma2/helm-charts.git
cd helm-charts
```
Set Up Your Kubernetes Context:
```
kubectl config use-context docker-desktop
```
Create a Namespace 
```
kubectl config use-context docker-desktop 
```
Install the Helm Chart:
```
helm install minio-test ./repos/stable/minio/ --namespace test-namespace
```
Verify the Installation:
```
kubectl get all --namespace test-namespace
```
Check logs:
```
kubectl logs -f pod/minio-test-minio-5b9895fdcd-wjnvh -n test-namespace
```
Access minio UI:
```
kubectl port-forward svc/minio-test-minio 9000:9000 -n test-namespace
```
Clean:
```
helm delete my-release --namespace test-namespace
kubectl delete namespace test-namespace
```

# NIRD minIO test:
Install auth helper
```
go install github.com/UNINETTSigma2/nird-toolkit-auth-helper@latest
nird-toolkit-auth-helper login
```
Edit and paste the token
```
~/.kube/config
```
Check is using the context
```
kubectl config get-contexts
```
Install 
```
helm install minio-test ./repos/stable/minio/ --namespace namespace
```
Check pods are running
```
kubectl get pods -n namespace
```
List releases:
```
helm list -n namespace
```

Print a description of pod
```
kubectl describe pod containername -n namespace
```

Login into pod:
```
kubectl exec containername -n namespace -c busybox -it -- /bin/sh
```

Check authorisation for specific service users, e.g.:
```
kubectl auth can-i --as=system:serviceaccount:fairtracks-ns10022k:prefect-worker watch events -n fairtracks-ns10022k
```
