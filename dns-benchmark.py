#!/usr/bin/env python3


# Copyright (c) 2020 Maxim Egorushkin. MIT License. See the full licence in file LICENSE.


import sys, os, re, time
import urllib.request
import csv
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile
from multiprocessing import Pool

encoding = "utf-8"
dig = "/usr/bin/dig"
re_dig_answer_count = re.compile(r", ANSWER: (\d+),")
re_dig_query_time = re.compile(r";; Query time: (\d+) usec")


def parse_majestic_million_csv(f, n):
	with open(f, newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			yield row['Domain']
			if n > 0:
				n -= 1
				if not n:
					break


def parse_dig_output(f):
	for line in f:
		m = re_dig_answer_count.search(line)
		if m:
			answer_count = int(m.group(1))
			continue
		m = re_dig_query_time.match(line)
		if m:
			usec = int(m.group(1))
			yield answer_count, usec


def write_all(f, data):
	if not isinstance(data, bytes):
		data = data.encode(encoding)
	while True:
		written = f.write(data)
		if written == len(data):
			break
		data = data[written:]


def benchmark_dns(args):
	dns, domains_file = args

	dig_cmd = dig
	if dns != "system":
		dig_cmd += " @" + dns
	dig_cmd += " -u -f " + domains_file

	errors = 0
	dig_usec = 0
	count = 0

	t0 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
	dig_proc = os.popen(dig_cmd)
	for answer_count, usec in parse_dig_output(dig_proc):
		errors += not answer_count
		dig_usec += usec
		count += 1
	t1 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
	dig_rc = dig_proc.close()
	if dig_rc:
		print("{}: dig terminated with code {}.".format(dns, dig_rc), file=sys.stderr)

	return count, errors, dig_usec, t1 - t0


def main():
	parser = ArgumentParser(description="Benchmark DNS query time.")
	parser.add_argument("-n", "--count", type=int, default=1000,
						help="The number of requests to make, 0 means no limit. Default is %(default)s.")
	parser.add_argument("-s", "--dns", default="system", metavar="IP",
						help="A comma-separated list of DNS server IP addresses. Default is %(default)s.")
	parser.add_argument("-S", "--serial", default=False, action="store_true",
						help="Don't query in parallel.")
	args = parser.parse_args()

	# Download Majestic Million csv.
	majestic_million_csv = "majestic_million.csv"
	base = "https://downloads.majesticseo.com/"
	if not os.access(majestic_million_csv, os.R_OK):
		urllib.request.urlretrieve(base + majestic_million_csv, majestic_million_csv)

	if args.count >= 100:
		print("It may take minutes, please wait...")

	# To invoke dig only once per dns make a temporary file with all the domain names for dig to query.
	with NamedTemporaryFile(buffering=(1024 * 1024)) as domains_file:
		for domain in parse_majestic_million_csv(majestic_million_csv, args.count):
			write_all(domains_file, domain + '\n')
		domains_file.flush()

		dnss = [s.strip() for s in args.dns.split(',')]
		benchmark_dns_args = zip(dnss, [domains_file.name] * len(dnss))
		if args.serial:
			results = map(benchmark_dns, benchmark_dns_args)
		else:
			results = Pool(len(dnss)).map(benchmark_dns, benchmark_dns_args) # Run benchmarks for different dns in parallel.
		results = list(results)

	print("            dns,    time,    queries,     errors")
	for dns, (count, errors, dig_usec, total_sec) in zip(dnss, results):
		print("{:>15s}, {:7.3f}, {:10}, {:10}".format(dns, dig_usec * 1e-6, count, errors))


if __name__ == "__main__":
	main()

# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: t
# coding: utf-8
# End:
