# select server (if not given)
if [ -z "$sshserver" ]
then

    # show server options
    for i in "${!sshserveroptions[@]}"; do 
        printf "%s\t%s\n" "$((i+1))" "${sshserveroptions[$i]}"
    done

    # check input
    printf "Nummer oder Adresse: "
    read input
    if [[ -n "$input" ]] && (("$input" >= 1 && "$input" <= ${#sshserveroptions[@]}))
    then
        # use string between brackets only
        input="${sshserveroptions[(($input-1))]}"
        regex='.*\((.*)\).*'
        if [[ $input =~ $regex ]]
        then
            sshserver="${BASH_REMATCH[1]}"
        fi
    else
        # use input directly
        sshserver="$input"
    fi

    # exit if server still empty
    [[ -z "$sshserver" ]] && exit
fi


# separate port (if given after colon) from server
regex="^(.*):([0-9]+)$"
if [[ $sshserver =~ $regex ]]
then
    sshserver="${BASH_REMATCH[1]}"
    sshport="${BASH_REMATCH[2]}"
else
    sshport=22
fi
echo "server: $sshserver port: $sshport"
