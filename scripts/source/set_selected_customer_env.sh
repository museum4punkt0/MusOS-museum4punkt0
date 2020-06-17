# execute customer script
# (which must define docker properties)
customerenvscript="../customer/$customer/define_env.sh"
if [[ ! -f "$customerenvscript" ]]
then
    echo "customer $customer not found"
    exit
fi
. "$customerenvscript"
