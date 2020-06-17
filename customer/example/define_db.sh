webserveroptions=(
    "development (http://localhost:4000)"
    "productive (http://your.productive.server.xy:4000)"
)

# define standard objects
. ../data/define_standard.sh
. ../data/define_museum.sh

# define custom objects
declare -a customfiles=(

    # exhibit types
    customer/example/data/type_example
)

jsonfiles=(${standardfiles[@]} ${museumfiles[@]} ${customfiles[@]})
