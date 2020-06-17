# execute customer script
# (which must define webserveroptions and jsonfiles)
customerdbscript="../customer/$customer/define_db.sh"
if [[ ! -f "$customerdbscript" ]]
then
    echo "customer $customer not found"
    exit
fi
. "$customerdbscript"
