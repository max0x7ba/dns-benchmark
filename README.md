# dns-benchmark
DNS query response latency benchmark.

It measures the total time it takes to make DNS queries for Alexa top 1000 websites. The queries are done sequentially to measure the worst case latency rather than throughput. `dig` command is used to make and time DNS queries to specific DNS servers.

# Usage
```
$ git clone https://github.com/max0x7ba/dns-benchmark.git
$ cd dns-benchmark
$ ./dns-benchmark.py -h
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
$ ./dns-benchmark.py --dns 8.8.8.8,1.1.1.1,81.139.57.100,192.168.50.1,system
It may take minutes, please wait...
            dns,    time,    queries,     errors
        8.8.8.8,  72.517,       1000,         17
        1.1.1.1,  20.850,       1000,         17
  81.139.57.100, 127.110,       1000,         17
   192.168.50.1,  21.186,       1000,         17
         system,  21.134,       1000,         17
```

In my setup system and router (192.168.50.1) DNS use Cloudflare DNS and this is why their times are similar.

---

Copyright (c) 2020 Maxim Egorushkin. MIT License. See the full licence in file LICENSE.
