I created this solution as I was finding it quite tedious to look up IPs for all nodes in a OKE nodepool.

It's easy to use, you first must have all your tenancy details in your ~/.oci/config. For example, I deal with a number 
of different tenancies. Example of ~/.oci/config:

```
[TENACY_NAME_1]
user=ocid1.user.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
fingerprint=00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
tenancy=ocid1.tenancy.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
region=us-ashburn-1
key_file=/path/to/your/oci-private.pem

[TENACY_NAME_2]
user=ocid1.user.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
fingerprint=00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
tenancy=ocid1.tenancy.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
region=us-ashburn-1
key_file=/path/to/your/oci-private.pem
```
Arguments you need to supply:
* -t tenancy_name name of tenancy label in your ~/.oci/config
* -c cluster OCI ID 
* -p pool_name Can be the full node pool name or partial. 

How to run the script:
python3 get_worker_nodes.py -t TENACY_NAME_1 -c ocid1.cluster.oc1.iad.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa -p stage-b

Output will list IPs per line for each worker node.

Please send suggestions to john.larsen@oracle.com
