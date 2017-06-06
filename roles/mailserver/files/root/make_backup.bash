#!/bin/bash
# make backup of tine20 database, mail and files
php /usr/share/tine20/setup.php -c /etc/tine20/ --backup -- config=1 db=1 files=1 backupDir=/root/backup
# make backup of mailinglist
tar cfvj /root/backup/$(ls -1t /root/backup/ | head -1)/mailman.tar.bz2 /var/lib/mailman
