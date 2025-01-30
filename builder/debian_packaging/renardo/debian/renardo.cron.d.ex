#
# Regular cron jobs for the renardo package.
#
0 4	* * *	root	[ -x /usr/bin/renardo_maintenance ] && /usr/bin/renardo_maintenance
