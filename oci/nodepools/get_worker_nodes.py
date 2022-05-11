import oci
import os
import yaml
import argparse

__author__      = "John Kip Larsen"
__copyright__   = "Copyright 2021"


def connect(region, tenancy):
    """ Connection to OCI. Its important that you have your ~/.oci/configs configured.

    Args:
        region (str): region name is pulled from cluster id.
        tenancy (str): Tenancy name must match [tenancy] in your ~/.oci/config

    Returns container engine object
    """
    config = oci.config.from_file(profile_name=tenancy)
    config['region'] = region

    return oci.container_engine.ContainerEngineClient(config)


def get_compartment_id(engine, cluster_id):
    """ Gets the department details which is needed to get the correct node.

    Args:
        engine (oci.container_engine.ContainerEngineClient object): Oci connection object
        cluster_id (str): oci ID of the cluster in question.

    Returns string of compartment ID.
    """
    get_cluster_response = engine.get_cluster(cluster_id=cluster_id)
    return get_cluster_response.data.compartment_id


def get_node_pools(engine, cluster_id, compartment_id):
    """ Gets the data from the nodepools.

    Args:
        engine (oci.container_engine.ContainerEngineClient object): Oci connection object
        cluster_id (str): oci ID of the cluster in question.
        compartment_id (str): Compartment id of cluster.

    Returns nodepool data
    """
    get_node_pools_response = engine.list_node_pools(compartment_id=compartment_id,
                                                     cluster_id=cluster_id)

    return get_node_pools_response.data


def get_static_config():
    """ Gets static config from yaml file
        proxy details
        dictionary of regions.

        Returns yaml object
    """
    with open('config.yaml', 'r') as f:
        d = yaml.load(f, Loader=yaml.FullLoader)

    return d


def get_user_args():
    """ Gets user supplied arguments.

    Returns arg.parse dictionary
    """
    parser = argparse.ArgumentParser(description='Arguments for getting worker node IPs from a cluster')
    parser.add_argument('-t', '--tenancy', help="name of tenancy used in your ~/.oci/config", required=True)
    parser.add_argument('-c', '--cluster', help="oci ID of your cluster", required=True)
    parser.add_argument('-p', '--pool', help="Searchable name of your pool."
                                             "Can be part of the name or full name.", required=True)
    args = parser.parse_args()

    return args


def get_compute_list(client, compartment_id):
    return oci.pagination.list_call_get_all_results(client.list_instances, compartment_id)


def set_env(env_data):
    """ Sets environment for proxy if needed.

    Args:
        env_data (str): Proxy details.
    """
    if env_data is None:
        pass
    else:
        proxy = env_data
        os.environ['HTTP_PROXY'] = proxy


def get_region(regions, cluster):
    """ Gets the region name from the cluster ID

    Args:
        regions (dictionary): dictionary of regions where shortname is the key to the long name value.
        cluster (str): the OCI ID of the cluster in question.

    Returns a string of the region long name.
    """
    region_short_name = cluster.split('.')[3]

    return regions[region_short_name]


def main(config, args):
    region = get_region(config['regions'], args.cluster)
    tenancy = args.tenancy
    cluster_id = args.cluster
    pool_name = args.pool

    engine = connect(region, tenancy)
    config = oci.config.from_file(profile_name=tenancy)
    config['region'] = region
    compartment_id = get_compartment_id(engine, cluster_id)
    pools_data = get_node_pools(engine, cluster_id, compartment_id)
    compute_client = oci.core.ComputeClient(config)
    network_client = oci.core.VirtualNetworkClient(config)

    for pool in pools_data:
        if pool_name in pool.name:
            compute_list = get_compute_list(compute_client, compartment_id)
            for instance in compute_list.data:
                if pool.id == instance.metadata.get('oke-pool-id'):
                    vnic_id = compute_client.list_vnic_attachments(compartment_id, instance_id=instance.id)
                    private_ip = network_client.get_vnic(vnic_id.data[0].vnic_id).data.private_ip

                    print(private_ip)


if __name__ == '__main__':
    config_data = get_static_config()
    user_args = get_user_args()
    set_env(config_data.get('proxy', None))
    main(config_data, user_args)
