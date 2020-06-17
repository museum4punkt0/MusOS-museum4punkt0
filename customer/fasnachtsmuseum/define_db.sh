webserveroptions=(
    "development (http://localhost:4000)"
)

# define standard objects
. ../data/define_standard.sh
. ../data/define_museum.sh

# define custom objects
declare -a customfiles=(

    # exhibit types
    customer/fnm/data/type_carnivalmask
    customer/fnm/data/type_carnivalcostume
    customer/fnm/data/type_carnivaltradition
    customer/fnm/data/type_carnivalart
    customer/fnm/data/type_carnivalwriting
    customer/fnm/data/type_carnivalmisc
    customer/fnm/data/type_carnivalboard
    customer/fnm/data/type_fnm_description
)

jsonfiles=(${standardfiles[@]} ${museumfiles[@]} ${customfiles[@]})
