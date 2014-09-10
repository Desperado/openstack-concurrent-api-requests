import time
import datetime
import threading
import uuid
import argparse

from cinderclient import client


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


def create_volume(size):

    current_time = datetime.datetime.utcnow().isoformat()
    volume_name = 'gaudeamus-volume-{}'.format(current_time)

    print cinder_cl.volumes.create(display_name=volume_name, size=size)


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
    parser.add_argument('-s', '--size', required=True,
                        help='Volume Size')
    parser.add_argument('-n', '--volumes', type=int, required=True,
                        help='Number of volumes to create')
    parser.add_argument('-l', '--load', type=int,
                        help='Number of simultaneous instance creation '
                             'requests to send')
    parser.add_argument('-a', '--sleep', type=int,
                        help='Amount of time to sleep between batches')

    args = parser.parse_args()

    cinder_cl = client.Client('1', args.user, args.password, args.tenant,
                              args.keystone_url)

    if args.load:
        batches = args.volumes / args.load
        batch_amount = args.load
        if batches == 0:
            batches = 1
            batch_amount = args.volumes
    else:
        batches = 1
        batch_amount = args.volumes

    for batch in range(batches):
        threads = []
        for i in range(batch_amount):
            thread = LogThread(target=create_volume,
                                      args=(args.size))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if args.sleep:
            # TODO: Don't sleep if this is the last batch
            print 'Sleeping for {} seconds'.format(args.sleep)
            time.sleep(args.sleep)
