#
# Regular cron jobs for the millisecond package.
#
0 4	* * *	root	[ -x /usr/bin/millisecond_maintenance ] && /usr/bin/millisecond_maintenance
