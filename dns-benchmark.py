#!/usr/bin/env python3


# Copyright (c) 2020 Maxim Egorushkin. MIT License. See the full licence in file LICENSE.


import sys, os, re, time, shutil, io
import urllib.request
import csv
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile
from multiprocessing import Pool
import multiprocessing
from subprocess import Popen, PIPE


def get_dig_path():
	cmd_result = shutil.which("dig")
	if cmd_result == None:
		raise OSError("dig tool not found")
	return cmd_result


encoding = "utf-8"
dig = get_dig_path()
re_dig_answer_count = re.compile(rb", ANSWER: (\d+),")
re_dig_query_time = re.compile(rb";; Query time: (\d+) usec")


def parse_majestic_million_csv(f, n):
	n = n if n > 0 else sys.maxsize
	with open(f, newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for i, row in enumerate(reader, 1):
			yield row['Domain']
			if i >= n:
				break


def parse_dig_output(f):
	for line in f:
		if m := re_dig_answer_count.search(line):
			answer_count = int(m.group(1))
		elif m := re_dig_query_time.match(line):
			usec = int(m.group(1))
			yield answer_count, usec


def parse_dig_outputs(dig_out_file):
	dig_usec = 0
	count = 0
	errors = 0
	for answer_count, usec in parse_dig_output(dig_out_file):
		errors += not answer_count
		dig_usec += usec
		count += 1
	return count, errors, dig_usec


def write_all(f, data):
	if not isinstance(data, bytes):
		data = data.encode(encoding)
	while data:
		written = f.write(data)
		data = data[written:]


def format_dig_cmd(args):
	dns, (domains_file, tls) = args

	dig_cmd = [dig]
	if tls:
		dig_cmd += ["+tls", "+notls-ca"]
	if dns != "system":
		dig_cmd += ["@" + dns]
	dig_cmd += ["-u", "-f", domains_file]

	return dig_cmd, dns


def benchmark_dns_file(args):
	dig_cmd, dns = format_dig_cmd(args)

	with NamedTemporaryFile() as dig_out_file:
		t0 = time.clock_gettime(time.CLOCK_MONOTONIC)
		# Save dig outputs into a file.
		with Popen(dig_cmd, stdout=dig_out_file) as dig_proc:
			dig_rc = dig_proc.wait()
			t1 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
		if dig_rc:
			print("{}: dig terminated with code {}.".format(dns, dig_rc), file=sys.stderr)

		# Parse dig outputs after dig completes.
		dig_out_file.seek(0)
		return *parse_dig_outputs(dig_out_file), t1 - t0


def benchmark_dns_pipe(args):
	dig_cmd, dns = format_dig_cmd(args)

	t0 = time.clock_gettime(time.CLOCK_MONOTONIC)
	# Save dig outputs into memory.
	with Popen(dig_cmd, stdout=PIPE) as dig_proc:
		dig_proc_out = dig_proc.stdout.read(-1)
		t1 = time.clock_gettime(time.CLOCK_MONOTONIC)

	# Parse dig outputs after dig completes.
	return *parse_dig_outputs(io.BytesIO(dig_proc_out)), t1 - t0


def main():
	parser = ArgumentParser(description="Benchmark DNS query time.")
	parser.add_argument("-n", "--count", type=int, default=1000,
						help="The number of requests to make, 0 means no limit. Default is %(default)s.")
	parser.add_argument("-s", "--dns", default="system", metavar="IP",
						help="A comma-separated list of DNS server IP addresses. Default is %(default)s.")
	parser.add_argument("-S", "--serial", action="store_true",
						help="Don't query in parallel.")
	parser.add_argument("-F", "--tmp", action="store_true",
						help="Use temporary files instead of pipes for more accurate timing of dig.")
	parser.add_argument("-T", "--tls", action="store_true",
						help="Use DNS-over-TLS queries.")
	args = parser.parse_args()

	# Download Majestic Million csv.
	majestic_million_csv = "majestic_million.csv"
	base = "https://downloads.majesticseo.com/"
	if not os.access(majestic_million_csv, os.R_OK):
		urllib.request.urlretrieve(base + majestic_million_csv, majestic_million_csv)

	if args.count >= 100:
		print(f"Making {args.count:,} DNS queries may take minutes, please wait...")

	benchmark_dns = benchmark_dns_file if args.tmp else benchmark_dns_pipe

	# To invoke dig only once per dns make a temporary file with all the domain names for dig to query.
	with NamedTemporaryFile(buffering=(1024 * 1024)) as domains_file:
		for domain in parse_majestic_million_csv(majestic_million_csv, args.count):
			write_all(domains_file, domain + '\n')
		domains_file.flush()

		dnss = [s.strip() for s in args.dns.split(',')]
		benchmark_dns_args = zip(dnss, [(domains_file.name, args.tls)] * len(dnss), strict=True)
		if args.serial:
			results = map(benchmark_dns, benchmark_dns_args)
		else:
			results = Pool(len(dnss)).map(benchmark_dns, benchmark_dns_args) # Run benchmarks for different dns in parallel.
		results = list(results)

	print("            dns,     time,    queries,     errors")
	for dns, (count, errors, dig_usec, total_sec) in zip(dnss, results):
		print("{:>15s}, {:7,.3f}s, {:10,}, {:10,}".format(dns, dig_usec * 1e-6, count, errors))


if __name__ == "__main__":
	main()

# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: t
# coding: utf-8
# compile-command: "cd ~/src/dns-benchmark && ./dns-benchmark.py --dns 8.8.8.8,1.1.1.1,192.168.50.1,system -n 2"
# End:
