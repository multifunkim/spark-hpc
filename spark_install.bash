#!/bin/bash
# 
# Installs SPARK
# 
# Last revision: August, 2019
# Maintainer: Obai Bin Ka'b Ali @aliobaibk
# License: In the app folder or check GNU GPL-3.0.



############## Function to install the MATLAB version
function install_spark_matlab() {
    output_dir="$1" && \
    \
    echo -e '\n\n\nInstalling SPARK for MATLAB...' && \
    \
    mkdir -p "$output_dir" && \
    app_dir="$output_dir"/spark-matlab && \
    if [ -d "$app_dir" ]; then
        echo ' - Found an existing MATLAB version of SPARK, deleting it...'
        rm -rf "$app_dir"/*
    else
        mkdir "$app_dir"
    fi && \
    tmp_dir="$(mktemp -d --tmpdir="$output_dir" tmp-XXXXX)" && \
    \
    echo ' - Downloading SPARK library (latest)...' && \
    wget -q "https://api.github.com/repos/multifunkim/spark-matlab/releases/latest" -O "$tmp_dir"/spark.latest && \
    zip_url="$(grep zipball_url "$tmp_dir"/spark.latest | cut -d '"' -f 4)" && \
    wget -q "$zip_url" -O "$tmp_dir"/spark-lib.zip && \
    unzip -q "$tmp_dir"/spark-lib.zip -d "$tmp_dir" && \
    mv "$tmp_dir"/multifunkim-spark-matlab*/* "$app_dir" && \
    rm -rf "$tmp_dir"/spark.latest "$tmp_dir"/spark-lib.zip "$tmp_dir"/multifunkim-spark-matlab* && \
    \
    echo ' - Downloading SPARK main function...' && \
    wget -q -P "$app_dir" "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/main/spark.m" && \
    \
    echo ' - Downloading SPARK utilities...' && \
    wget -q -P "$app_dir"/util "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/prependFileToFile.m" && \
    wget -q -P "$app_dir"/util "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/str2RegSpacedVector.m" && \
    mkdir "$app_dir"/util/psom_gb && \
    wget -q -P "$app_dir"/util/psom_gb "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/psom_gb/spark_psom_gb.m" && \
    \
    echo ' - Downloading NIAK library (v0.16.0)...' && \
    wget -q -O "$tmp_dir"/niak-lib.zip "https://github.com/SIMEXP/niak/releases/download/v0.16.0/niak-with-dependencies.zip" && \
    mkdir "$app_dir"/externals && \
    unzip -q "$tmp_dir"/niak-lib.zip -d "$app_dir"/externals && \
    rm -f "$tmp_dir"/niak-lib.zip && \
    wget -q -O "$app_dir"/externals/niak*/extensions/psom*/psom_run_script.m "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/externals/psom_run_script.m" && \
    \
    rm -rf "$tmp_dir" && \
    \
    echo -e ' - All done, check:\n'"$app_dir"
}



############## Function to install the GNU Octave version
function install_spark_octave() {
    output_dir="$1" && \
    \
    echo -e '\n\n\nInstalling SPARK for GNU Octave...' && \
    \
    mkdir -p "$output_dir" && \
    app_dir="$output_dir"/spark-octave && \
    if [ -d "$app_dir" ]; then
        echo ' - Found an existing GNU Octave version of SPARK, deleting it...'
        rm -rf "$app_dir"/*
    else
        mkdir "$app_dir"
    fi && \
    tmp_dir="$(mktemp -d --tmpdir="$output_dir" tmp-XXXXX)" && \
    \
    echo ' - Downloading SPARK library (latest)...' && \
    wget -q "https://api.github.com/repos/multifunkim/spark-matlab/releases/latest" -O "$tmp_dir"/spark.latest && \
    zip_url="$(grep zipball_url "$tmp_dir"/spark.latest | cut -d '"' -f 4)" && \
    wget -q "$zip_url" -O "$tmp_dir"/spark-lib.zip && \
    unzip -q "$tmp_dir"/spark-lib.zip -d "$tmp_dir" && \
    mv "$tmp_dir"/multifunkim-spark-matlab*/* "$app_dir" && \
    rm -rf "$tmp_dir"/spark.latest "$tmp_dir"/spark-lib.zip "$tmp_dir"/multifunkim-spark-matlab* && \
    \
    echo ' - Downloading SPARK main function...' && \
    wget -q -P "$app_dir" "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/main/spark.m" && \
    \
    echo ' - Downloading SPARK utilities...' && \
    wget -q -P "$app_dir"/util "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/prependFileToFile.m" && \
    wget -q -P "$app_dir"/util "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/str2RegSpacedVector.m" && \
    mkdir "$app_dir"/util/psom_gb && \
    wget -q -P "$app_dir"/util/psom_gb "https://raw.githubusercontent.com/multifunkim/spark-hpc/master/for_build/app_extra/util/psom_gb/spark_psom_gb.m" && \
    \
    echo ' - Downloading NIAK library (v1.1.4)...' && \
    wget -q -O "$tmp_dir"/niak-lib.zip "https://github.com/SIMEXP/niak/releases/download/v1.1.4/niak-with-dependencies.zip" && \
    mkdir "$app_dir"/externals && \
    unzip -q "$tmp_dir"/niak-lib.zip -d "$app_dir"/externals && \
    rm -f "$tmp_dir"/niak-lib.zip && \
    \
    rm -rf "$tmp_dir" && \
    \
    echo -e ' - All done, check:\n'"$app_dir"
}



############## Function to install the Singularity version
function install_spark_sing() {
    output_dir="$1" && \
    \
    echo -e '\n\n\nInstalling SPARK for Singularity...' && \
    \
    mkdir -p "$output_dir" && \
    app_dir="$output_dir"/spark-singularity && \
    if [ -d "$app_dir" ]; then
        echo ' - Found an existing Singularity version of SPARK, deleting it...'
        rm -rf "$app_dir"/*
    else
        mkdir "$app_dir"
    fi && \
    tmp_dir="$(mktemp -d --tmpdir=/var/tmp tmp-XXXXX)" && \
    \
    pushd "$app_dir" >/dev/null 2>&1 && \
    export SINGULARITY_CACHEDIR="$tmp_dir" && \
    export SINGULARITY_LOCALCACHEDIR="$tmp_dir" && \
    export SINGULARITY_TMPDIR="$tmp_dir" && \
    export SINGULARITY_PULLFOLDER="$tmp_dir" && \
    singularity build spark-hpc.simg docker://multifunkim/spark-hpc && \
    popd >/dev/null 2>&1 && \
    \
    rm -rf "$tmp_dir" && \
    \
    echo -e '\n - All done, check:\n'"$app_dir"
}



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
check_existant_app_file "$this_loc"/spark_argparse.py



############## Checking the inputs and getting info
oargs="$("$this_loc"/spark_argparse.py "$@")"
if [[ $? != 0 ]]; then
    echo -e "\n\n\n     ***** Something went wrong"
    echo -e "\n     Closing the program\n"
    exit 1
    
elif help_requested "$@"; then
    echo "$oargs"
    exit 0
    
fi



############## Reading info
output_dir="$(echo "$oargs" | cut -d '"' -f 2)"
versions="$(echo "$oargs" | cut -d '"' -f 4)"



############## Installing

if [[ "$versions" == *"matlab"* ]] || [[ "$versions" == *"all"* ]]; then
    install_spark_matlab "$output_dir"
fi

if [[ "$versions" == *"octave"* ]] || [[ "$versions" == *"all"* ]]; then
    install_spark_octave "$output_dir"
fi

if [[ "$versions" == *"singularity"* ]] || [[ "$versions" == *"all"* ]]; then
    SING_VERSION=$(singularity --version 2>&1)
    if ! is_ver_higher "$SING_VERSION" "2.5.2"; then
        echo -e "\n\n\n         ***** Singularity 2.5.2+ is required"
        echo -e "Error when running 'singularity --version':\n""$SING_VERSION"
        echo -e "\n         Cannot install the Singularity version of SPARK"
        echo -e "\n         Closing the program\n"
        exit 1
    fi
    install_spark_sing "$output_dir"
fi


