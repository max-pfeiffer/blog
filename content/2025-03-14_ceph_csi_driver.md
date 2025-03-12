Title: Using Ceph CSI Driver for Kubernetes
Description: A guide for configuring a Ceph cluster and Ceph CSI driver as Kubernetes storage solution   
Summary: A guide for configuring a Ceph cluster and Ceph CSI driver as Kubernetes storage solution
Date: 2025-03-14 12:00
Author: Max Pfeiffer
Lang: en
Keywords: Ceph, Ceph CSI, Container Storage Interface, Kubernetes, Storage, Volumes, PVC
Image: https://max-pfeiffer.github.io/blog/images/2025-02-28_oauth2_proxy_simplified-architecture.svg




## Ceph cluster configuration
### Configuration for RBD CSI Driver
The configuration for the RBD CSI driver [is well documented](https://docs.ceph.com/en/reef/rbd/rbd-kubernetes/).
You need to create a new pool and initialize it:
```shell
$ ceph osd pool create kubernetes
pool 'kubernetes' created
$ rbd pool init kubernetes
```

Then create the user for the RBD CSI driver [with these capabilities](https://github.com/ceph/ceph-csi/blob/devel/docs/capabilities.md#rbd):
```shell
$ ceph auth get-or-create client.kubernetes \
  mon 'profile rbd' \
  osd 'profile rbd pool=kubernetes' \
  mgr 'profile rbd pool=kubernetes'
[client.kubernetes]
	key = KAHDKLJDLiowejfnKjdflgmjdlfmreogkfrgmi9tmn==
```
Grab that key. You will need it later for configuring the driver.

### Configuration for CephFS CSI Driver
[Create pools for CephFS](https://docs.ceph.com/en/reef/cephfs/createfs/#creating-pools):
```shell
$ ceph osd pool create cephfs_data
$ ceph osd pool create cephfs_metadata
```

Then [create the filesystem itself based on these two pools](https://docs.ceph.com/en/reef/cephfs/createfs/#creating-a-file-system):
```shell
$ ceph fs new cephfs cephfs_metadata cephfs_data
```

Create a user for the CephFS CSI driver with [these capabilities](https://github.com/ceph/ceph-csi/blob/devel/docs/capabilities.md#cephfs):
```shell
$ ceph auth get-or-create client.kubernetes-cephfs \
  mgr 'allow rw' \
  osd 'allow rw tag cephfs metadata=cephfs, allow rw tag cephfs data=cephfs' \
  mds 'allow r fsname=cephfs path=/volumes, allow rws fsname=cephfs path=/volumes/csi' \
  mon 'allow r fsname=cephfs'
```
Also grab that key.
