import argparse

from novaclient.v1_1 import client


def delete_instances():
    for server in nova_cl.servers.list():
        if server.name.startswith('gaudeamus-instance'):
            print server.delete()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keystone_url', required=True,
                        help='Keystone endpoint URL')
    parser.add_argument('-u', '--user', required=True,
                        help='Keystone username')
    parser.add_argument('-p', '--password', required=True,
                        help='Keystone password')
    parser.add_argument('-t', '--tenant', required=True,
                        help='Keystone tenant name')

    args = parser.parse_args()

    nova_cl = client.Client(args.user, args.password, args.tenant,
                            args.keystone_url, service_type='compute')

    delete_instances()