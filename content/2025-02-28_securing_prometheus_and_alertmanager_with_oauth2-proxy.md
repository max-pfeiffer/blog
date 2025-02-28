Title: Securing Prometheus and Alertmanager web UI with oauth2-proxy and Keycloak
Description: How to configure a secure login for your Prometheus and Alertmanger web UI with oauth2-proxy and Keycloak
Summary: How to configure a secure login for your Prometheus and Alertmanger web UI with oauth2-proxy and Keycloak
Date: 2025-02-28 15:00
Author: Max Pfeiffer
Lang: en
Keywords: Prometheus, Alertmanager, oauth2-proxy, Keycloak, SSO, Single Sign On
Image: https://max-pfeiffer.github.io/blog/images/2025-02-07_keycloak_client_scopes_evaluate.png

[Prometheus](https://prometheus.io/) and [Alertmanager](https://github.com/prometheus/alertmanager) come with a quite
useful web user interface. But other than [Grafana](https://grafana.com/) there is no build in mechanism for user
authentication or authorization. In an [earlier article]({filename}/2025-02-07_sso_for_grafana_with_keycloak.md) I was
covering that single sign on (SSO) configuration for [Grafana](https://grafana.com/) with [Keycloak](https://www.keycloak.org/).
A nice option to configure SSO for [Prometheus](https://prometheus.io/) and [Alertmanager](https://github.com/prometheus/alertmanager)
is to use the [oauth2-proxy project](https://github.com/oauth2-proxy/oauth2-proxy) for it.

![2025-02-28_oauth2_proxy_simplified-architecture.svg]({static}/images/2025-02-28_oauth2_proxy_simplified-architecture.svg)
_Image source: https://github.com/oauth2-proxy/oauth2-proxy/blob/master/docs/static/img/simplified-architecture.svg_

[oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) offers two integration options: running it as reverse
proxy or as middleware. In a Kubernetes environment with an ingress controller, it makes much more sense to run it as
middleware and let it just handle the authentication challenges. How that works is well described in
[its official documentation](https://oauth2-proxy.github.io/oauth2-proxy/behaviour).

## Preliminary decisions
For doing the configuration, we need to do some decisions first:

1. ingress configuration for Prometheus and Altermanager: on what domains or URL paths would we like to run these applications
2. [oauth2-proxy integration](https://oauth2-proxy.github.io/oauth2-proxy/#architecture): reverse proxy or middleware (see above)
3. [oauth2-proxy session storage](https://oauth2-proxy.github.io/oauth2-proxy/configuration/session_storage): cookie or Redis

### Ingress configuration decision
It's quite common to run Prometheus and Alertmanager (and also Grafana) on a single monitoring domain with different
paths, i.e.:

* monitoring.yourcompany.com/prometheus
* monitoring.yourcompany.com/alertmanager
* monitoring.yourcompany.com/grafana

This is done for good reasons:

* you just need to have one domain for your cluster's monitoring
* that way you just need to configure and run a single instance of oauth2-proxy, oauth2-proxy is just not made for
  covering multiple domains with a single installation.
* permission configuration: permission concept for users is usually bound equally to the Kube-Prometheus stack 
* it's convenient for users to access the different applications in this manner

So we will follow that common approach and use one domain and different URL paths for the applications.

### oauth2-proxy integration decision
In a Kubernetes environment you usually run an ingress controller handling the incoming network traffic. In my case,
I use the [ingress-nginx](https://github.com/kubernetes/ingress-nginx). There you have
[good options to forward authentication requests to oauth2-proxy using the `auth_request` directive](https://oauth2-proxy.github.io/oauth2-proxy/configuration/integration#configuring-for-use-with-the-nginx-auth_request-directive)
and use it as middleware. So we go for this option as it is very flexible and easy to configure with ingress
annotations.

### oauth2-proxy session storage decision
oauth2-proxy has two options for storing the session information for authenticated users: in a cookie or in
[Redis database](https://redis.io/). Actually [ingress-nginx](https://github.com/kubernetes/ingress-nginx) has problems
looping through large cookies in headers and requires some sophisticated configuration to make that work.
Storing the session information in [Redis database](https://redis.io/) is in overall a more solid solution and avoids
additional network payload. But it uses additional Kubernetes computing resources and consumes storage (if persisted).
But it's easy and convenient to configure the Redis variant using the 
[Helm chart for oauth2-proxy](https://github.com/oauth2-proxy/manifests), so I decided to go with this solution.

## Keycloak configuration
I assume that you have a running [Keycloak](https://www.keycloak.org/) installation in your Kubernetes cluster. In an
earlier article, I was covering the [automated provisioning of Keycloak with OpenTofu]({filename}/2025-01-10_how_to_configure_keycloak_terraform_provider.md).


## Ingress controller configuration


## oauth2-proxy installation
There is a [Helm chart for oauth2-proxy](https://github.com/oauth2-proxy/manifests) which is well maintained by the
community. Is used without any issues to install [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) in my
Kubernetes cluster.