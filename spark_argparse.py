#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Checks the inputs for installing SPARK (meant to be used with the SPARK installer BASH script)
# 
# Last revision: August, 2019
# Maintainer: Obai Bin Ka'b Ali @aliobaibk
# License: In the app folder or check GNU GPL-3.0.



from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime
import os
from sys import argv
from sys import exit as sys_exit
from textwrap import dedent



def setup_versions(versions):
    """Makes one string out of the input list of versions
    """

    if type(versions) is str:
        return versions
    elif len(versions) == 1 and type(versions) is list:
        return versions[0]
    else:
        return ' '.join(versions)



def setup_abspath(output_dir):
    """Makes sure all paths are absolute.
    """
    
    return os.path.abspath(output_dir)



def check_iargs_parser(iargs):
    """Defines the possible arguments of the program, generates help and usage messages,
    and issues errors in case of invalid arguments.
    """
    
    parser = ArgumentParser(
        description=dedent('''\
        SParsity-based Analysis of Reliable K-hubness (SPARK)
        ____________________________________________________________________________________
         
           8b    d8 88   88 88     888888 88     888888 88   88 88b 88 88  dP 88 8b    d8
           88b  d88 88   88 88       88   88     88__   88   88 88Yb88 88odP  88 88b  d88
           88YbdP88 Y8   8P 88  .o   88   88     88""   Y8   8P 88 Y88 88"Yb  88 88YbdP88
           88 YY 88 `YbodP' 88ood8   88   88     88     `YbodP' 88  Y8 88  Yb 88 88 YY 88
           ------------------------------------------------------------------------------
                              Multimodal Functional Imaging Laboratory
        ____________________________________________________________________________________
         
        '''),
        formatter_class=RawTextHelpFormatter,
        add_help=False)

    parser.add_argument('-h',
                        action='help',
                        help=dedent('''\
                        Shows this help message and exits.
                        ____________________________________________________________
                        '''))
    parser.add_argument('-d', '--output-dir', nargs=1, type=str,
                        default='.',
                        help=dedent('''\
                        The directory (absolute or relative) where to install SPARK.
                        If not specified, then the current directory will be used.

                        Notes:
                        - The directory 'Multi_FunkIm' will be created and all
                        selected versions of SPARK will be installed in it.
                        - If the directory 'Multi_FunkIm' already exists with
                        existing version(s) of SPARK in it, then the existing
                        version(s) might get deleted.
                         
                        (default: %(default)s)
                        (type: %(type)s)
                        ____________________________________________________________
                        '''),
                        metavar=('X'),
                        dest='output_dir')
    parser.add_argument('-v', '--versions', nargs='+', type=str,
                        choices=['all', 'matlab', 'octave', 'singularity'], 
                        default='all',
                        help=dedent('''\
                        The version(s) of SPARK to install.

                        Notes:
                        - To install the Singularity version, you will need the
                        application 'Singularity 2.5.2+'
                        - The MATLAB version of SPARK comes with NIAK BOSS v0.16.0.
                        - The GNU Octave version of SPARK comes with NIAK v1.1.4.
                         
                        (valid values: %(choices)s)
                        (default: %(default)s)
                        (type: %(type)s)
                        ____________________________________________________________
                        '''),
                        metavar=('X'),
                        dest='versions')
    
    oargs = vars(parser.parse_args(iargs))

    # Hack: when (nargs=1) a list should not be returned
    if type(oargs['output_dir']) is list:
        oargs['output_dir'] = oargs['output_dir'][0]

    return oargs



def check_iargs(iargs):
    """Checks the integrity of the input arguments and returns the options if successful
    """
    
    oargs = check_iargs_parser(iargs)
    oargs['output_dir'] = setup_abspath(oargs['output_dir'])
    oargs['versions'] = setup_versions(oargs['versions'])
    return oargs



def main(iargs):
    """Main function, checks the inputs to compile BEst and prints the info for the compiling routine
    """

    oargs = check_iargs(iargs)

    print('"' + os.sep.join([oargs['output_dir'], 'Multi_FunkIm']) + '" "'  + oargs['versions'] + '"')

    return sys_exit(0)



############## Main
if __name__ == "__main__":
    main(argv[1:])
    