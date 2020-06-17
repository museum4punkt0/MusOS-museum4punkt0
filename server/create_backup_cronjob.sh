#!/usr/bin/env bash


if [[ $# -eq 0 ]] ; then
    echo 'Please call this script with a customer as parameter, e.g. create_backup_cronjob cxn'
    exit 0
fi

# get installation directory of this instance
install_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"

# create a backup cronjob if it is not already present
echo "Creating backup cronjob..."
croncmd="cd ${install_dir}/scripts/ ; ${install_dir}/scripts/backup_musos.sh --customer $1 --docker `which docker` > ${install_dir}/../backup.log 2>&1"
cronjob="0 3 * * * $croncmd"
( crontab -l | grep -v -F "backup_musos" ; echo "$cronjob" ) | crontab -

echo "Executing backup once to test the connection and add the host key to known_hosts..."
cd ${install_dir}/scripts/
${install_dir}/scripts/backup_musos.sh --customer $1 --docker `which docker`