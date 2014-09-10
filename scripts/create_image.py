import time
import datetime
import threading
import argparse
import urllib2
import os

from glanceclient import Client as gl_client
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


def download_image():

    url = "https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img"

    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()


def create_image():
    current_time = datetime.datetime.utcnow().isoformat()

    image_name = 'gaudeamus-image-{}'.format(current_time)

    with open('cirros-0.3.0-x86_64-disk.img') as fimage:
        image = glance.images.create(name=image_name, is_public=False, disk_format="qcow2",
        container_format="bare", data=fimage)

    print "Image {} status: {}".format(image_name, image.status)

    image.delete()


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
    parser.add_argument('-n', '--images', type=int, required=True,
                        help='Number of images to create')
    parser.add_argument('-l', '--load', type=int,
                        help='Number of simultaneous image creation '
                             'requests to send')
    parser.add_argument('-a', '--sleep', type=int,
                        help='Amount of time to sleep between batches')

    args = parser.parse_args()

    auth_client = ks_client.Client(username=args.user, password=args.password,
                            tenant_name=args.tenant,
                            auth_url=args.keystone_url)
    glance_endpoints = \
        auth_client.service_catalog.get_endpoints('image', 'public')

    glance_url = glance_endpoints['image'][0]['publicURL']
    glance = gl_client('1', endpoint=glance_url, token=auth_client.auth_token)
    download_image()


    if args.load:
        batches = args.images / args.load
        batch_amount = args.load
        if batches == 0:
            batches = 1
            batch_amount = args.images
    else:
        batches = 1
        batch_amount = args.images

    for batch in range(batches):
        threads = []
        for i in range(batch_amount):
            thread = threading.Thread(target=create_image)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if args.sleep:
            # TODO: Don't sleep if this is the last batch
            print 'Sleeping for {} seconds'.format(args.sleep)
            time.sleep(args.sleep)

    os.remove("cirros-0.3.0-x86_64-disk.img")