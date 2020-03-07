# dns-benchmark
DNS query response time benchmark.

# Usage
```
$ git clone https://github.com/max0x7ba/dns-benchmark.git
$ cd dns-benchmark
$ ./dns-benchmark.py
Report for system default dns:
	queries: 1000
	errors: 16
	total time dig: 102.265 seconds
	total time: 110.437 seconds

$ ./dns-benchmark.py --dns 8.8.8.8
Report for dns 8.8.8.8:
	queries: 1000
	errors: 16
	total time dig: 57.918 seconds
	total time: 66.291 seconds


$ ./dns-benchmark.py --dns 1.1.1.1
Report for dns 1.1.1.1:
	queries: 1000
	errors: 16
	total time dig: 27.971 seconds
	total time: 36.170 seconds
```
