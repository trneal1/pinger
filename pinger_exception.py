#! /usr/bin/python3
import socket
import time
from icmplib import multiping, resolve, NameLookupError
import threading
import logging

testid = 'base11'

hosts = [
    'p1.lan', 'p2.lan', 'p3.lan', 'walert.lan', 'RokuStreamingStick.lan',
    'esp_a_b.lan', 'esp_a_l.lan', 'esp_a_t.lan', 'esp_a_s.lan', 'Rokustick-754.lan',
    'esp_th_a.lan', 'esp_th_g.lan', 'esp_th_u.lan', 'esp_th_d.lan', 'esp_sdc40.lan',
    'esp_tft.lan', 'esp_tft1.lan', 'esp_tft2.lan', 'Livingroom.lan', 'esp_mpu6050.lan',
    'esp_clock.lan', 'esp_load_mon.lan', 'esp_a_g.lan', 'RE220.lan', ''
]

addresses = ['0'] * 25
counts = [0] * 25
lastdrop = [0] * 25

logger = logging.getLogger(__name__)
logging.basicConfig(filename='pinger.log', level=logging.INFO)
logger.info('Started')

# @tl.job(interval=timedelta(seconds=10 * 60))
def stats():
    while True:
        print('{')
        for i in range(25):
            print(
                '{\'id\':%d,\'host\':\'%s\',\'address\':\'%s\',\'count\':%d}' % (i, hosts[i], addresses[i], counts[i]))
        print('}')
        time.sleep(10 * 60)

# @tl.job(interval=timedelta(seconds=10 * 60))
def resolver():
    while True:
        for i in range(25):
            try:
                addresses[i] = resolve(hosts[i])[0]
            except NameLookupError:
                addresses[i] = '245.0.0.0'
        time.sleep(10 * 60)

# @tl.job(interval=timedelta(seconds=10))
def ping():
    iteration=0
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('pinger.lan', 3100))
            sock1.connect(('trneal-Green-G2.lan', 9001))

            iteration = iteration + 1
            resp = multiping(addresses, count=2, interval=0.5, timeout=1.0, privileged=False)

            for i in range(25):
                if hosts[i] == '':
                    sock.send(bytes('%d 1000 14x222200 0x000000\n' % (24 - i), 'utf-8'))
                elif addresses[i] == '245.0.0.0':
                    sock.send(bytes('%d 1000 14x000022 0x000000\n' % (24 - i), 'utf-8'))
                elif resp[i].is_alive and (counts[i] == 0 or (iteration - lastdrop[i] > 6 * 10)):
                    sock.send(bytes('%d 1000 14x002200 0x000000\n' % (24 - i), 'utf-8'))
                elif resp[i].is_alive and counts[i] > 0:
                    sock.send(bytes('%d 1000 14x220000 0x000000\n' % (24 - i), 'utf-8'))
                else:
                    sock.send(bytes('%d 500 220000 000000\n' % (24 - i), 'utf-8'))
                    sock1.send(bytes('{\'testid\':\'%s\',\'id\':%d,\'hostname\':\'%s\',\'address\':\'%s\'}\n\n' % (
                        testid, i, hosts[i], addresses[i]), 'utf-8'))
                    counts[i] = counts[i] + 1
                    lastdrop[i] = iteration
                    print(hosts[i])
            time.sleep(8)
        except Exception as e:
            print('An exception occurred:', e)
            logger.info(f'Exception: {e}')
        finally:
            sock.close()
            sock1.close()

t1 = threading.Thread(target=stats, name='stats')
t2 = threading.Thread(target=resolver, name='resolver')
t3 = threading.Thread(target=ping, name='ping')

t2.start()
t3.start()
t1.start()

while True:
    time.sleep(60)
