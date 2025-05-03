Title: Overhauling my Ceph cluster 
Description: Upgrading all Raspberry Pi 5 with NVMe HAT supporting two SSDs, re-installing Ceph cluster, Vlan configuration    
Summary: Upgrading all Raspberry Pi 5 with NVMe HAT supporting two SSDs, re-installing Ceph cluster, Vlan configuration
Date: 2025-05-03 12:00
Author: Max Pfeiffer
Lang: en
Keywords: Ceph, Raspberry Pi 5, Vlan
Image: https://max-pfeiffer.github.io/blog/images/2025-03-08_overhauling_my_ceph_cluster.jpeg

I decided to optimize and secure my network setup. As part of this new configuration, I decided to put my Ceph cluster
into a separate network and use a Vlan.


![2025-03-08_overhauling_my_ceph_cluster.jpeg]({static}/images/2025-03-08_overhauling_my_ceph_cluster.jpeg)

Enter a shell using cephadm:
```shell
$ cephadm shell
$ ceph orch device ls --wide --refresh
HOST   PATH          TYPE  TRANSPORT  RPM  DEVICE ID                              SIZE  HEALTH  IDENT  FAULT  AVAILABLE  REFRESHED  REJECT REASONS                                                           
ceph1  /dev/nvme0n1  ssd                   KINGSTON_SNV3S1000G_50026B73831D5E2F   931G          N/A    N/A    No         6m ago     Has a FileSystem, Insufficient space (<10 extents) on vgs, LVM detected  
ceph2  /dev/nvme0n1  ssd                   KINGSTON_SNV3S1000G_50026B7785C1AC00   931G          N/A    N/A    No         6m ago     Has a FileSystem, Insufficient space (<10 extents) on vgs, LVM detected  
ceph3  /dev/nvme0n1  ssd                   KINGSTON_SNV3S1000G_50026B7785C1ABFC   931G          N/A    N/A    No         6m ago     Has a FileSystem, Insufficient space (<10 extents) on vgs, LVM detected
```
Zap the SSDs on all hosts:
```shell
$ ceph orch device zap ceph1 /dev/nvme0n1 --force
zap successful for /dev/nvme0n1 on ceph1
$ ceph orch device zap ceph2 /dev/nvme0n1 --force
zap successful for /dev/nvme0n1 on ceph2
$ ceph orch device zap ceph3 /dev/nvme0n1 --force
zap successful for /dev/nvme0n1 on ceph3
$ ceph orch device ls --wide --refresh
HOST   PATH          TYPE  TRANSPORT  RPM  DEVICE ID                              SIZE  HEALTH  IDENT  FAULT  AVAILABLE  REFRESHED  REJECT REASONS  
ceph1  /dev/nvme0n1  ssd                   KINGSTON_SNV3S1000G_50026B73831D5E2F   931G          N/A    N/A    Yes        3m ago                     
ceph2  /dev/nvme0n1  ssd                   KINGSTON_SNV3S1000G_50026B7785C1AC00   931G          N/A    N/A    Yes        3m ago                     
ceph3  /dev/nvme0n1  ssd                   KINGSTON_SNV3S1000G_50026B7785C1ABFC   931G          N/A    N/A    Yes        3m ago                     
```
Add all SSDs as storage devices to the Ceph cluster:
```shell
$ ceph orch apply osd --all-available-devices
Scheduled osd.all-available-devices update...
```