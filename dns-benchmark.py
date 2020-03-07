#!/usr/bin/env python3

import argparse, sys, os, re, time

def parse_alexa_top_csv(f, n):
	for line in f:
		domain = line[line.index(",") + 1:].strip()
		yield domain
		if n:
			n -= 1
			if not n:
				break

def parse_dig_output(f):
	re_dig_answer_count = re.compile(", ANSWER: (\d+),")
	re_query_time = re.compile(";; Query time: (\d+) msec")
	for line in f:
		m = re_dig_answer_count.search(line)
		if m:
			answer_count = int(m.group(1))
			continue
		m = re_query_time.match(line)
		if m:
			msec = int(m.group(1))
			return answer_count, msec

	raise RuntimeError("Failed to parse dig output.");

def main():
	parser = argparse.ArgumentParser(description="Benchmark DNS query time.")
	parser.add_argument("-n", "--count", type=int, default=1000, help="The number of requests to make, 0 means unlimited. Default is %(default)s.")
	parser.add_argument("-s", "--dns", help="DNS server to use, default is the system default one.")
	parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Increase logging verbosity.")
	args = parser.parse_args()

	alexa_top_csv = "top-1m.csv"
	if not os.access("top-1m.csv", os.R_OK):
		os.system("wget -O top-1m.csv.zip http://s3.amazonaws.com/alexa-static/top-1m.csv.zip && unzip top-1m.csv.zip && rm top-1m.csv.zip")

	dig = "/usr/bin/dig "
	if args.dns:
		dig += "@" + args.dns + " "

	errors = 0
	total_msec = 0
	count = 0
	t0 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
	for domain in parse_alexa_top_csv(open(alexa_top_csv), args.count):
		if args.verbose:
			print(domain, end=" ... ")
		dig_proc = os.popen(dig + domain)
		answer_count, msec = parse_dig_output(dig_proc)
		errors += not answer_count
		total_msec += msec
		assert not dig_proc.close()
		count += 1
		if args.verbose:
			print(msec, "msec")
	t1 = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)

	if args.dns:
		print("Report for dns", args.dns + ":")
	else:
		print("Report for system default dns:")
	print("\tqueries:", count)
	print("\terrors:", errors)
	print("\ttotal time dig: {:.3f} seconds".format(total_msec / 1000))
	print("\ttotal time: {:.3f} seconds".format(t1 - t0))

if __name__ == "__main__":
	main()

# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: t
# coding: utf-8
# End:
