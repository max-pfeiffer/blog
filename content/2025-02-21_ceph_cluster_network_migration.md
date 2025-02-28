Title: Migrating a Ceph Cluster to a different Network 
Description: How to migrate a Ceph Cluster running on Ubuntu 24.04 to a different network
Summary: How to migrate a Ceph Cluster running on Ubuntu 24.04 to a different network
Date: 2025-02-21 16:00
Author: Max Pfeiffer
Lang: en
Keywords: Ceph, Ubuntu, Network, Migration
Image: https://max-pfeiffer.github.io/blog/images/2025-01-20_bootstrap_certificate_authority.jpeg


## Prerequisites 

Ubuntu packages: ceph-common, ceph-base
https://docs.ceph.com/en/reef/cephadm/operations/#client-keyrings-and-configs


## Stop the cluster
https://docs.ceph.com/en/reef/rados/operations/operating/#stopping-all-daemons


## Get the monitor map

```shell
$ ceph mon getmap -o /tmp/monitormap
$ monmaptool --print monitormap
monmaptool: monmap file monitormap
epoch 3
fsid 1df5d6ca-c048-11ef-ab4c-2ccf671c56b5
last_changed 2024-12-22T10:47:39.266961+0100
created 2024-12-22T10:36:41.516385+0100
min_mon_release 19 (squid)
election_strategy: 1
0: [v2:192.168.1.90:3300/0,v1:192.168.1.90:6789/0] mon.ceph1
1: [v2:192.168.1.91:3300/0,v1:192.168.1.91:6789/0] mon.ceph2
2: [v2:192.168.1.92:3300/0,v1:192.168.1.92:6789/0] mon.ceph3
```

## Change the monitor map
You need to remove the existing monitors from that map first:
```shell
$ monmaptool --rm ceph1 --rm ceph2 --rm ceph3 monitormap
```
Then you can add the monitors with the new network configuration:
```shell
$ monmaptool --addv ceph1 [v2:192.168.30.10:3300,v1:192.168.30.10:6789] --addv ceph2 [v2:192.168.30.11:3300,v1:192.168.30.11:6789] --addv ceph3 [v2:192.168.30.12:3300,v1:192.168.30.12:6789] monitormap
```
Check the results:
```shell
monmaptool --print monitormap 
monmaptool: monmap file monitormap
epoch 3
fsid 1df5d6ca-c048-11ef-ab4c-2ccf671c56b5
last_changed 2024-12-22T10:47:39.266961+0100
created 2024-12-22T10:36:41.516385+0100
min_mon_release 19 (squid)
election_strategy: 1
0: [v2:192.168.30.10:3300/0,v1:192.168.30.10:6789/0] mon.ceph1
1: [v2:192.168.30.11:3300/0,v1:192.168.30.11:6789/0] mon.ceph2
2: [v2:192.168.30.12:3300/0,v1:192.168.30.12:6789/0] mon.ceph3
```