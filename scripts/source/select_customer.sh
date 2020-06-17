# select customer (if not given)
if [[ -z "$customer" ]]
then

    # show options
    ls ../customer/

    # check input
    printf "Customer-Kürzel: "
    read customer

    # exit if customer still empty
    [[ -z "$customer" ]] && exit
fi
echo "customer: $customer"
