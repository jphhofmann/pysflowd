# pysflowd - sflow collector and analyzer

pysflowd is a python based sflow collector and analyzer, which aims to gain information about peak load towards single ip-addresses (or networks).

## Application structure

pysflowd has the following operational scheme:

1. Read configuration file in /etc/pysflowd.conf
2. Create SQLite3 in-memory database
3. Spawn collector thread, which opens a udp socket on the desired ip/port
4. Spawn analyzer thread(s), check SQLite3 contents against configured limits

## Thirdparty code

pysflowd relies on auspex-labs sflow-collector library, which provides pysflowd with the required sflow packet parser.

See https://github.com/auspex-labs/sflow-collector for more details.

## Questions, Ideas, etc.

Feel free to contact me (jh@combahton.net).
