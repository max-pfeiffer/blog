Title: How to Bootstrap a Certificate Authority in your Kubernetes Cluster 
Description: A guide for bootstrapping a certificate authority for issuing TLS certificates in a Kubernetes cluster   
Summary: A guide for bootstrapping a certificate authority for issuing TLS certificates in a Kubernetes cluster
Date: 2025-01-19 11:00
Author: Max Pfeiffer
Lang: en
Keywords: CA, certificate authority, Step CA, Step Issuer, cert-manager, bootstrap, Kubernetes, TLS

In overall, I was a bit unhappy using self-signed TLS certificates in my home lab Kubernetes cluster. I found it
annoying to click away these warnings in my browser. Also, I ran into a couple of problems using self-signed
certificates for my [Keycloak](https://www.keycloak.org/) installation. When configuring SSO for
[ArgoCD](https://argoproj.github.io/cd/) and [Grafana](https://grafana.com/) I had to configure security overrides when
calling Keycloak OIDC endpoints for the authentication process. So I decided to create my owm certificate authority
eventually.

A friend recommended the solution from [Smallstep](https://smallstep.com/) to me. These guys provide
[Step CA](https://github.com/smallstep/certificates) which is a piece of software which issues TLS certificates
based on your own root certificate authority (CA). They also provide
[Step Issuer](https://github.com/smallstep/step-issuer) which is a Kubernetes [cert-manager](https://cert-manager.io)
[CertificateRequest](https://cert-manager.io/docs/usage/certificaterequest) controller that uses
[Step CA](https://github.com/smallstep/certificates).

Installing [Step CA](https://github.com/smallstep/certificates) and [Step Issuer](https://github.com/smallstep/step-issuer)
und configuring Ingresses with it, I fell into a couple of traps and encountered an annoying bug. So that process was
not as straight forward as I thought and I spent a while on a working solution. So I guess it's worth sharing my
experience with the public.

## Step CA
I was using the [Helm chart to install Step CA](https://artifacthub.io/packages/helm/smallstep/step-certificates).
As a first step you want to create your `values.yaml` file.
[Smallstep offers a CLI tool](https://github.com/smallstep/cli) which comes in handy here. It's quickly
[installed](https://smallstep.com/docs/step-cli/installation/) on your machine. You can generate your `values.yaml`
like so:
```shell
step ca init --helm > step-ca-values.yaml
```
This will result in some interactive process where you need to enter the following configuration options:

1. Deployment Type: you want to select `Standalone` here
2. Name od the PKI: pick something that suits you
3. DNS names: here you need to have a FQDN for:
   1. cert-manager (mandatory): this needs to be some FQDN that your
      [internal Kubernetes DNS can resolve](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/),
      i.e. `step-certificates.security.svc.cluster.local` or `step-certificates.cert` **depending on the namespace you
      will install it into**
   2. the outside world: if you choose to offer that service on some public domain i.e. `ca.yourdomain.com`
4. IP and port: go with the default `:443` or pick whatever matches your use case
5. First provisioner name: as we are aiming for cert-manager using it, `cert-manager` is probably a good choice
6. Password: when you generate one, it ends up base64encoded in that `values.yaml` file

Depending on how you conduct the installation process with Helm, you might want to remove the password and
certificates, keep it in your credential store and inject it later with your provisioning tool. I use
[OpenTofu](https://opentofu.org/) for this. A simple install using Helm CLI can be done like this:
```shell
helm repo add smallstep https://smallstep.github.io/helm-charts/
helm install step-certificates smallstep/certificates -f step-ca-values.yaml --namespace security
```
Please be aware of the `security` namespace. This will result in Step Certificates being available under the FQDN
`step-certificates.security.svc.cluster.local` in your Kubernetes cluster. As you probably don't want to install and
run it in your default namespace, this is this first trap you can fall into.

## Results
Now check for ConfigMaps created by that Helm chart:
```shell
$ kubectl -n security get configmap
NAME                       DATA   AGE
kube-root-ca.crt           1      42h
step-certificates-certs    2      42h
step-certificates-config   4      42h
```
And have a closer look at that `step-certificates-certs` ConfigMap:
```shell
kubectl -n security get configmap step-certificates-certs -o yaml
```
Take note that includes the root_ca certificate. This will come in handy later.

Also check on the `step-certificates-config` ConfigMap:
```shell
kubectl -n security get configmap step-certificates-config -o yaml
```
Take note that it includes the configuration for the provisioner that we generated with the
[Step CLI tool]((https://github.com/smallstep/cli)) earlier. We will need that later to configure the
[Step Issuer](https://github.com/smallstep/step-issuer).

Check on the Secrets which were created by the Helm chart:
```shell
$ kubectl -n security get secret                                   
NAME                                      TYPE                                 DATA   AGE
sh.helm.release.v1.step-certificates.v1   helm.sh/release.v1                   1      42h
step-certificates-ca-password             smallstep.com/ca-password            1      42h
step-certificates-provisioner-password    smallstep.com/provisioner-password   1      42h
step-certificates-secrets                 smallstep.com/private-keys           2      42h
```
Take not that there is a secret containing the provisioner password `step-certificates-provisioner-password`. This
we also need to configure the [Step Issuer](https://github.com/smallstep/step-issuer).

## Step Issuer