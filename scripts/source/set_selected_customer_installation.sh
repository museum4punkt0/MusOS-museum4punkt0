# execute customer script
# (which must define sshserveroptions and directories)
customerinstallationscript="../customer/$customer/define_installation.sh"
if [[ ! -f "$customerinstallationscript" ]]
then
    echo "customer $customer not found"
    exit
fi
. "$customerinstallationscript"
