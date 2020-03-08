# dns-benchmark
DNS query response latency benchmark.

It measures the total time it takes to make DNS queries for Alexa top 1000 websites. The queries are done sequentially to measure the worst case latency rather than throughput.

It uses `dig` command to make and time DNS queries to specific dns servers.

There are normally a few layers of DNS caching, depending on one's network setup:

* In the operating system.
* In the router.
* In ISP.

A command line option allows to specify multiple DNS servers to

multiple DNS server latencies the DNS servers should be arranged from the farthest to the closest one on the command line, so that a closer DNS doesn't make its parent DNS cached records.

# Usage
```
$ git clone https://github.com/max0x7ba/dns-benchmark.git
$ cd dns-benchmark
$ $ ./dns-benchmark.py -h
usage: dns-benchmark.py [-h] [-n COUNT] [-s IP]

Benchmark DNS query time.

optional arguments:
  -h, --help            show this help message and exit
  -n COUNT, --count COUNT
                        The number of requests to make, 0 means no limit. Default is 1000.
  -s IP, --dns IP       A comma-separated list of DNS server IP addresses. Default is system.
```

In the following example I measure the latencies of Google (8.8.8.8), Cloudflare (1.1.1.1), ISP (81.139.57.100), router (192.168.50.1) and system DNSs. The time is reported in seconds.

```
$ ./dns-benchmark.py --dns 8.8.8.8,1.1.1.1,81.139.57.100
It may take minutes, please wait...
            dns,    time,    queries,     errors
        8.8.8.8,  71.601,       1000,         16
        1.1.1.1,  24.080,       1000,         16
  81.139.57.100, 130.268,       1000,         16

$ ./dns-benchmark.py --dns 192.168.50.1
It may take minutes, please wait...
            dns,    time,    queries,     errors
   192.168.50.1,  42.669,       1000,         16

$ ./dns-benchmark.py
It may take minutes, please wait...
            dns,    time,    queries,     errors
         system,  24.740,       1000,         16
```
