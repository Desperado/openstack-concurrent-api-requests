import argparse

from cinderclient import client


def delete_volumes():
    for volume in cinder_cl.volumes.list():
        if volume.display_name.startswith('gaudeamus-volume'):
            print volume.delete()


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

    cinder_cl = client.Client('1', args.user, args.password, args.tenant,
                              args.keystone_url)

    delete_volumes()
