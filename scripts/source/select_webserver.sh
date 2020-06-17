# select server (if not given)
if [ -z "$webserver" ]
then

    # show server options
    for i in "${!webserveroptions[@]}"; do 
        printf "%s\t%s\n" "$((i+1))" "${webserveroptions[$i]}"
    done

    # check input
    printf "Nummer oder Adresse: "
    read input
    if [[ -n "$input" ]] && (("$input" >= 1 && "$input" <= ${#webserveroptions[@]}))
    then
        # use string between brackets only
        input="${webserveroptions[(($input-1))]}"
        regex='.*\((.*)\).*'
        if [[ $input =~ $regex ]]
        then
            webserver="${BASH_REMATCH[1]}"
        fi
    else
        # use input directly
        webserver="$input"
    fi

    # exit if server still empty
    [[ -z "$webserver" ]] && exit
fi
echo "webserver: $webserver"