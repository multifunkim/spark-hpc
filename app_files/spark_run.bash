#!/bin/bash
# 
# Runs SPARK
# 
# Last revision: August, 2019
# Maintainer: Obai Bin Ka'b Ali @aliobaibk
# License: In the app folder or check GNU GPL-3.0.



############## Function to check if help was requested
function help_requested() {
    [[ "$@" =~ (^|[[:space:]])"-h"($|[[:space:]]) ]] || \
    [[ "$@" =~ (^|[[:space:]])"--help"($|[[:space:]]) ]]
}



############## Function to check if an application file is present
function check_existant_app_file() {
    filepath="$1"
    filename="$2"

    if [ ! -f "$filepath" ]; then
        echo -e "\n     - The file $filename is missing"
        echo -e "\n     Please make sure you have the complete application"
        echo -e "\n     For help, please check (or report a bug at):\nhttps://github.com/multifunkim/spark-hpc"
        exit 1
    fi
}



############## Function to compare software versions
function is_ver_higher() {
python3 - "$1" "$2" << END
from sys import exit as sys_exit
try:
    from distutils.version import StrictVersion
    from re import compile
    from sys import argv

    regex = compile('([0-9]+\.)+[0-9]+')
    ver = regex.search(argv[1]).group(0)
    ref_ver = regex.search(argv[2]).group(0)
    if int(StrictVersion(ver) >= StrictVersion(ref_ver)):
        sys_exit(0)
    else:
        sys_exit(1)
except Exception as err:
    from sys import stderr
    print('Error when checking software versions:\n' + str(err), file=stderr)
    sys_exit(1)
END
    [[ $? == 0 ]]
}



############## Preliminary check: Python 3+
PY_VERSION="$(python3 --version 2>&1)"
if ! is_ver_higher "$PY_VERSION" "3.0"; then
    echo -e "\n\n\n     ***** Python 3+ is required"
    echo -e "Error when running 'python3 --version':\n"$PY_VERSION
    echo -e "\n     Closing the program\n"
    exit 1
fi



############## Checking for the application files
this_loc="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
check_existant_app_file "$this_loc"/spark_setup.py spark_setup.py
check_existant_app_file "$this_loc"/frames/matlab.bash matlab.bash
check_existant_app_file "$this_loc"/frames/sing.bash sing.bash



############## Checking the inputs and getting formatted info
oargs="$("$this_loc"/spark_setup.py "$@")"
if [[ $? != 0 ]]; then
    echo -e "\n\n\n     ***** Something went wrong"
    echo -e "\n     Closing the program\n"
    exit 1
    
elif help_requested "$@"; then
    echo "$oargs"
    exit 0
    
fi



############## Reading formatted info
main_job=""
interactive=""
scheduler=""
jobs_ctrl_spec=""


while IFS=' ' read -ra cmd; do
    case "${cmd[0]}" in
    
    'main_job')
        main_job="${cmd[@]:1}"
        ;;
    
    'interactive')
        interactive="${cmd[@]:1}"
        ;;
    
    'scheduler')
        scheduler="${cmd[@]:1}"
        ;;
        
    'jobs_ctrl_spec')
        jobs_ctrl_spec="${cmd[@]:1}"
        ;;
        
    esac
done < "$oargs"


if [[ -z "$main_job" ]]; then
    echo "Failed to read the main job file"
    exit 1

elif [[ -z "$interactive" ]]; then
    echo "Failed to read the interactive flag"
    exit 1
    
elif [[ -z "$scheduler" ]]; then
    echo "Failed to read the scheduler"
    exit 1

fi



############## Main
chmod u+x "$main_job"
if [[ "$scheduler" == "SGE" ]] || [[ "$scheduler" == "TORQUE" ]]; then
    if [[ $interactive == 1 ]]; then
        qrsh $jobs_ctrl_spec "$main_job"
    else
        "$main_job"
    fi
elif [[ $scheduler == 'SLURM' ]]; then
    if [[ $interactive == 1 ]]; then
        srun $jobs_ctrl_spec "$main_job"
    else
        "$main_job"
    fi
elif [[ $scheduler == 'NONE' ]]; then
    "$main_job"
fi