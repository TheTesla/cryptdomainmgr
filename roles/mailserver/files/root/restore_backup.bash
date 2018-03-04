#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters - please specify date of backup to restore"
    exit 1
fi

# make backup before restore
/root/make_backup.bash
# restore tine20 with database, mail and files
php /usr/share/tine20/setup.php -c /etc/tine20/ --restore -- config=1 db=1 files=1 backupDir=/root/backup/$1
# restore backup of mailinglist
tar xfvj /root/backup/$1/mailman.tar.bz2 -C /var/lib/mailman


