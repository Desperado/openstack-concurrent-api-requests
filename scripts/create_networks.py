import time
import datetime
import threading
import argparse

from neutronclient.neutron import client as neutron_client
from keystoneclient.v2_0 import client as ks_client


class LogThread(threading.Thread):
    """LogThread should always e used in preference to threading.Thread.

    The interface provided by LogThread is identical to that of threading.Thread,
    however, if an exception occurs in the thread the error will be logged
    (using logging.exception) rather than printed to stderr.

    This is important in daemon style applications where stderr is redirected
    to /dev/null.

    """
    def __init__(self, **kwargs):
        super(LogThread, self).__init__(**kwargs)
        self._real_run = self.run
        self.run = self._wrap_run

    def _wrap_run(self):
        try:
            self._real_run()
        except Exception, e:
            exit(1)
            print Exception('Exception during LogThread.run - %s' % e)


def create_network():
    current_time = datetime.datetime.utcnow().isoformat()

    neutron.format = 'json'
    network_name = 'gaudeamus-mynetwork-{}'.format(current_time)
    network = {'name': network_name, 'admin_state_up': True}
    neutron.create_network({'network': network})
    networks = neutron.list_networks(name=network_name)
    print networks
    network_id = networks['networks'][0]['id']
    neutron.delete_network(network_id)



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
    parser.add_argument('-n', '--networks', type=int, required=True,
                        help='Number of networks to create')
    parser.add_argument('-l', '--load', type=int,
                        help='Number of simultaneous network creation '
                             'requests to send')
    parser.add_argument('-a', '--sleep', type=int,
                        help='Amount of time to sleep between batches')

    args = parser.parse_args()

    auth_client = ks_client.Client(username=args.user, password=args.password,
                            tenant_name=args.tenant,
                            auth_url=args.keystone_url)
    neutron_endpoints = \
        auth_client.service_catalog.get_endpoints('network', 'public')

    neutron_url = neutron_endpoints['network'][0]['publicURL']
    neutron = neutron_client.Client('2.0', endpoint_url=neutron_url, token=auth_client.auth_token)

    if args.load:
        batches = args.networks / args.load
        batch_amount = args.load
        if batches == 0:
            batches = 1
            batch_amount = args.networks
    else:
        batches = 1
        batch_amount = args.networks

    for batch in range(batches):
        threads = []
        for i in range(batch_amount):
            thread = LogThread(target=create_network)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if args.sleep:
            # TODO: Don't sleep if this is the last batch
            print 'Sleeping for {} seconds'.format(args.sleep)
            time.sleep(args.sleep)
