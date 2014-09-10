openstack-concurrent-api-requests
=================================

These scripts can be used to stress test the openstack cloud system

**WARNING** Be careful of running these scripts on production and parent, they can critically influence system performance

This project provides scripts to give a simple stress tests on core platform services: compute, volume, image and network.

1. **Authentication**

All scripts accepts keystone *Identity URL* as -k, *username* as -u, *password* as -p and tenant -p. Also all scripts accept *number of parallel batches* as -n.

2. **Creating instances.**

To create instance you should provide *flavor id* as -f, and *image id* as -i.::

    python create_instance.py -k {v2 endpoint} -u {username} -p {password} -t {tenant} -f 1 -i {image_id} -n 10

To delete instance, you should do::

    python delete_instance.py -k {v2 endpoint} -u {username} -p {password} -t {tenant}

3. **Creating volumes.**

Additionaly from authentication, only size is provided as -s (in Gb). This script will create 10 volumes with 1Gb in parallel.::

    python create_volume.py -k {v2 endpoint} -u {username} -p {password} -t {tenant} -s 1 -n 10

To delete volumes, you should do::

    python delete_volume.py -k {v2 endpoint} -u {username} -p {password} -t {tenant}

4. **Creating images.**

All images are created from Cirros. Only number of images should be provided as -n. So each time new cirros iso is downloaded, test runs and then image is delete from filesystem.::

    python create_image.py -k {v2 endpoint} -u {username} -p {password} -t {tenant} tempest -n 10

5. **Creating networks.**

Script accepts only number of networks to be created as -n.::

    python create_network.py -k {v2 endpoint} -u {username} -p {password} -t {tenant} -t tempest -n 20