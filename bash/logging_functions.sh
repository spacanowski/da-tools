##################################################
############# Logging functions ##################
##################################################

function _print_color {
    local COLOR=$1
    local msg=$2
    local NC='\033[0m'

    echo -e "${COLOR}${msg}${NC}"
}

function _error {
    local error=$1
    local RED='\033[0;31m'

    _print_color "${RED}" "${error}"

    exit 1
}

function _warn {
    local warning=$1
    local YELLOW='\033[1;33m'

    _print_color "${YELLOW}" "${warning}"
}

function _info {
    local warning=$1
    local BLUE='\033[0;34m'

    _print_color "${BLUE}" "${warning}"
}

function _succes {
    local msg=$1
    local GREEN='\033[0;32m'

    _print_color "${GREEN}" "${msg}"
}
