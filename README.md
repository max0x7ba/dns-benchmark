# dns-benchmark
DNS query response latency benchmark.

It measures the total time it takes to make DNS queries for Alexa top 1000 websites. The queries are done sequentially to measure the worst case latency rather than throughput. `dig` command is used to make and time DNS queries to specific DNS servers.

# Usage
```bash
git clone https://github.com/max0x7ba/dns-benchmark.git   # clone the repo
cd dns-benchmark                                          # go into cloned directory
./dns-benchmark.py -h                                     # display help
```
```
(output - do not copy)
usage: dns-benchmark.py [-h] [-n COUNT] [-s IP] [-S]

Benchmark DNS query time.

optional arguments:
  -h, --help            show this help message and exit
  -n COUNT, --count COUNT
                        The number of requests to make, 0 means no limit. Default is 1000.
  -s IP, --dns IP       A comma-separated list of DNS server IP addresses. Default is system.
  -S, --serial          Don't query in parallel.
```

In the following example I measure the latencies of Google (8.8.8.8), Cloudflare (1.1.1.1), router (192.168.50.1) and system DNSs. The time is reported in seconds.

```bash
./dns-benchmark.py --dns 8.8.8.8,1.1.1.1,192.168.50.1,system
```
```
(output - do not copy)
It may take minutes, please wait...
            dns,    time,    queries,     errors
        8.8.8.8,  56.633,       1000,         16
        1.1.1.1,  12.089,       1000,         15
   192.168.50.1,   8.679,       1000,         15
         system,  13.443,       1000,         15
```

In my setup, system and router (192.168.50.1) DNS use Cloudflare DNS and this is why their times are similar. The router times are the best because it runs `dnsmasq` that caches DNS responses and is able to resolve some of the queries locally.

# Portability
The script requires Python 3 and `dig` command line utility.

It has been tested on:

* [Ubuntu Linux 18.04 LTS](https://ubuntu.com/download/desktop).
* [Ubuntu Linux 22.04 LTS](https://ubuntu.com/download/desktop).
* [Fedora 41](https://fedoramagazine.org/announcing-fedora-linux-41/).
* Windows 10 with [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) and Ubuntu Linux 18.04 LTS.
* Android 10 phone with [Termux](https://termux.com/) terminal emulator. Requires installing `git`, `dig`, `python` in Termux and using `--serial` command line option.
* [macOS 10.15](https://en.wikipedia.org/wiki/MacOS_Catalina)
* [macOS 15](https://en.wikipedia.org/wiki/MacOS_Sequoia)
* [FreeBSD 13.4](https://www.freebsd.org/releases/13.4R/announce/).

---

Copyright (c) 2020 Maxim Egorushkin. MIT License. See the full licence in file LICENSE.
