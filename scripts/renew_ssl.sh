#!/bin/bash

# Run daily on crontab e.g.
#  Your cron job will be run at: (5 times displayed)
#
#    2021-11-08 11:10:00 UTC
#    2021-11-09 11:10:00 UTC
#    2021-11-10 11:10:00 UTC
#    2021-11-11 11:10:00 UTC
#    2021-11-12 11:10:00 UTC
#    ...etc

#25 11 * * * /bin/bash /home/web/qgis-feed/scripts/renew_ssl.sh > /tmp/ssl-renewal-logs.txt
#Dont remove this blank line below !!!!!!!!!!! (make sure to leave a blank line at the end of the file)



/usr/local/bin/docker-compose -f /home/web/qgis-feed/docker-compose-production-ssl.yml run certbot renew \
&& /usr/local/bin/docker-compose -f /home/web/qgis-feed/docker-compose-production-ssl.yml kill -s SIGHUP nginx
