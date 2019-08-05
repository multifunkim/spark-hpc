#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Sets up SPARK
# 
# Last revision: August, 2019
# Maintainer: Obai Bin Ka'b Ali @aliobaibk
# License: In the app folder or check GNU GPL-3.0.



from argparse import ArgumentParser, RawTextHelpFormatter
from errno import EEXIST
import os
from shutil import copyfile
from sys import argv, stderr
from sys import exit as sys_exit
from textwrap import dedent
from tempfile import mkdtemp, mkstemp



def setup_entrypoint_opt(main_job, interactive, scheduler, jobs_ctrl_spec, tmp_dir):
    """Output to be read by the application entrypoint
    """
    
    entrypoint_opt = os.sep.join([tmp_dir, 'entrypoint.opt'])
    with open(entrypoint_opt, 'w') as file:
        file.write(
            'main_job ' + main_job + '\n' +
            'interactive ' + str(int(interactive)) + '\n' +
            'scheduler ' + scheduler + '\n' +
            'jobs_ctrl_spec ' + jobs_ctrl_spec + '\n'
            )
        
    if not os.path.isfile(entrypoint_opt):
        print('Failed to create/edit the options file for the application entrypoint:\n' + entrypoint_opt, file=stderr)
        sys_exit(1)
    
    return entrypoint_opt



def setup_main_job_sing(cmd_template, spark_exe, scheduler, pipe_opt, app_spec, tmp_dir):
    """Sets up the main job for running SPARK Singularity version
    """

    main_job = os.sep.join([tmp_dir, 'main_job.bash'])
    if os.path.isfile(main_job):
        os.remove(main_job)
        
    bash_var = '\n\n\n'\
        'scheduler="' + scheduler + '"\n' + \
        'tmp_dir="' + tmp_dir + '"\n' + \
        'fifo="' + app_spec['fifo'] + '"\n' + \
        'sing_binds="' + app_spec['sing_binds'] + '"\n' + \
        'sing_home="' + app_spec['sing_home'] + '"\n' + \
        'jobs_log="' + app_spec['jobs_log'] + '"\n'
    
    bash_cmd = ' \\\n' + \
        'exec -B "' + app_spec['sing_binds'] + '" -H "' + app_spec['sing_home'] + '":"' + app_spec['sing_home'] + '" "' + \
        spark_exe + '" ' + \
        '/bin/bash -c "' + \
        'export PSOM_FIFO=\'' + app_spec['fifo'] + '\' && ' + \
        'octave --no-gui -q --persist --eval \\"spark(\'' + pipe_opt + '\')\\""'

    ipath = os.sep.join([os.path.dirname(__file__), 'frames', 'sing.bash'])
    with open(ipath, 'r', newline='\n') as ifile:
        with open(main_job, 'w+', newline='\n') as ofile:
            num_lines = sum(1 for line in open(cmd_template, 'r', newline='\n'))
            for line in ifile:
                if not line.startswith('VAR_INS'):
                    ofile.write(line)
                else:
                    # Append the beginning of the command file
                    with open(cmd_template, 'r', newline='\n') as tmp_file:
                        c = 0
                        for line in tmp_file:
                            c += 1
                            if c != num_lines:
                                ofile.write(line)
                    ofile.write(bash_var)
            # Append the end of the command file
            with open(cmd_template, 'r', newline='\n') as tmp_file:
                c = 0
                for line in tmp_file:
                    c += 1
                    if c == num_lines:
                        ofile.write(line)
            ofile.write(bash_cmd)

    if not os.path.isfile(main_job):
        print('Failed to create/edit the main job to run SPARK (Singularity):\n' + main_job, file=stderr)
        sys_exit(1)

    return main_job



def setup_main_job_matlab(cmd_template, spark_exe, pipe_opt, tmp_dir):
    """Sets up the main job for running SPARK MATLAB version
    """

    main_job = os.sep.join([tmp_dir, 'main_job.bash'])
    if os.path.isfile(main_job):
        os.remove(main_job)
        
    matlab_cmd = ' \\\n-nodisplay -nosplash -r ' + \
        '"addpath(genpath(\'' + spark_exe + '\')), spark(\'' + pipe_opt + '\')"'

    ipath = os.sep.join([os.path.dirname(__file__), 'frames', 'matlab.bash'])
    with open(ipath, 'r', newline='\n') as ifile:
        with open(main_job, 'w+', newline='\n') as ofile:
            for line in ifile:
                if not line.startswith('VAR_INS'):
                    ofile.write(line)
                else:
                    # Append the command file
                    with open(cmd_template, 'r', newline='\n') as tmp_file:
                        for line in tmp_file:
                            ofile.write(line)
                        ofile.write(matlab_cmd)

    if not os.path.isfile(main_job):
        print('Failed to create/edit the main job to run SPARK (MATLAB):\n' + main_job, file=stderr)
        sys_exit(1)

    return main_job



def setup_main_job(version, cmd_template, spark_exe, scheduler, pipe_opt, app_spec, tmp_dir):
    """Sets up the main job (pipeline controller)
    """

    if 'matlab' in version:
        main_job = setup_main_job_matlab(cmd_template, spark_exe, pipe_opt, tmp_dir)
    elif 'singularity' in version:
        main_job = setup_main_job_sing(cmd_template, spark_exe, scheduler, pipe_opt, app_spec, tmp_dir)

    return main_job



def setup_jobs_log(tmp_dir):
    """Creates a temporary file for keeping the ID of submitted jobs
    """

    jobs_log = os.sep.join([tmp_dir, 'jobs.log'])
    with open(jobs_log, 'w+', newline='\n') as file:
        pass
        
    if not os.path.isfile(jobs_log):
        print('Failed to create the jobs ID file:\n' + jobs_log, file=stderr)
        sys_exit(1)
    
    return jobs_log



def setup_sing_home(out_dir):
    """Builds the home directory for the Singularity command
    """

    return out_dir



def setup_sing_binds(fmri_data, mask):
    """Builds the binding paths for the Singularity command
    """
    
    paths = set(
        [os.path.dirname(x[-1]) for x in fmri_data] + 
        [os.path.dirname(mask)])

    return ','.join(paths)



def setup_fifo(tmp_dir):
    """Creates a FIFO
    """

    fifo = os.sep.join([mkdtemp(prefix='fifo-', dir=tmp_dir), 'fifo'])
    os.mkfifo(fifo)
    
    if not os.path.exists(fifo):
        print('Failed to create a FIFO:\n' + fifo, file=stderr)
        sys_exit(1)
    
    return fifo



def setup_app_spec(iargs, tmp_dir):
    """Application specific options (depending on the SPARK version to use)
    For the Singularity version: sets up directories and files and builds the arguments of the Singularity command
    For the MATLAB version: nothing for now
    """

    app_spec = dict()
    if not 'singularity' in iargs['version']:
        return app_spec
    else:
        app_spec['sing_binds'] = setup_sing_binds(iargs['fmri_data'], iargs['mask'])
        app_spec['sing_home'] = setup_sing_home(iargs['out_dir'])
        if 'scheduler' in iargs['version']:
            app_spec['fifo'] = setup_fifo(tmp_dir)
            app_spec['jobs_log'] = setup_jobs_log(tmp_dir)
        else:
            app_spec['fifo'] = ''
            app_spec['jobs_log'] = ''

    return app_spec



def setup_pipe_opt(iargs, tmp_dir):
    """Builds the list of options for running the SPARK analyses with GNU Octave/MATLAB
    The options will be read by the GNU Octave/MATLAB SPARK main function
    """

    pipe_opt = os.sep.join([tmp_dir, 'pipe.opt'])
    with open(pipe_opt, 'w', newline='\n') as file:
        file.write(
            'fmri_data ' + ' , '.join([' '.join(data) for data in iargs['fmri_data']]) + '\n' +
            'mask ' + iargs['mask'] + '\n' +
            'out_dir ' + iargs['out_dir'] + '\n' +
            'nb_resamplings ' + str(iargs['nb_resamplings']) + '\n' +
            'network_scales ' + ' '.join([str(x) for x in iargs['network_scales']]) + '\n' +
            'nb_iterations ' + str(iargs['nb_iterations']) + '\n' +
            'p_value ' + str(iargs['p_value']) + '\n' +
            'resampling_method ' + iargs['resampling_method'] + '\n' +
            'block_window_length ' + ' '.join([str(x) for x in iargs['block_window_length']]) + '\n' +
            'dict_init_method ' + iargs['dict_init_method'] + '\n' +
            'sparse_coding_method ' + iargs['sparse_coding_method'] + '\n' +
            'preserve_dc_atom ' + str(int(iargs['preserve_dc_atom'])) + '\n' +
            'verbose ' + str(int(iargs['verbose'])) + '\n' +
            'psom_gb ' + iargs['psom_gb'] + '\n'
            )
        
    if not os.path.isfile(pipe_opt):
        print('Failed to create/edit the SPARK pipeline options file:\n' + pipe_opt, file=stderr)
        sys_exit(1)
    
    return pipe_opt



def setup_psom_gb(ipsom_gb, version, spark_exe, scheduler, jobs_spec, max_parallel_jobs, tmp_dir):
    """Appropriately copies the PSOM configuration file into a folder that will be added to GNU Octave/MATLAB path and edits it
    """

    psom_gb_dir = os.sep.join([tmp_dir, 'psom-gb'])
    try:
        os.mkdir(psom_gb_dir)
    except OSError as e:
        if e.errno != EEXIST:
            print('Failed to create the PSOM configuration directory:\n' + psom_gb_dir + '\n' + str(e), file=stderr)
            sys_exit(1)

    opsom_gb = os.sep.join([psom_gb_dir, 'psom_gb_vars_local.m'])
    if os.path.isfile(opsom_gb):
        os.remove(opsom_gb)
    if ipsom_gb:
        copyfile(ipsom_gb, opsom_gb)

    with open(opsom_gb, 'a', newline='\n') as file:
        file.write("\n\n\n%% Automatic")
        
        if 'matlab' in version:
            #file.write("\ngb_psom_init_matlab = 'rehash toolboxcache';")
            if 'scheduler' in version:
                file.write("\ngb_psom_mode = 'qsub';")
            else:
                file.write("\ngb_psom_mode = 'background';") # Should be default
            if scheduler == 'SLURM':
                file.write("\nsetenv('PSOM_HACK_SLURM','1');")
        elif 'singularity' in version:
            file.write("\ngb_psom_singularity_image = '" + spark_exe + "';")
            if 'scheduler' in version:
                file.write("\ngb_psom_mode = 'singularity';")
            else:
                file.write("\ngb_psom_mode = 'background';") # Should be default

        if 'scheduler' in version and jobs_spec:
            if scheduler == 'SGE' or scheduler == 'TORQUE':
                file.write("\ngb_psom_qsub_options = '-V " + jobs_spec + "';")
            elif scheduler == 'SLURM':
                file.write("\ngb_psom_qsub_options = '--export=ALL " + jobs_spec + "';")

        file.write("\ngb_psom_max_queued = " + str(max_parallel_jobs) + ";" +
                   "\ngb_psom_tmp = ['" + tmp_dir + "', filesep];")

    if not os.path.isfile(opsom_gb):
        print('Failed to create/edit the PSOM configuration file:\n' + opsom_gb, file=stderr)
        sys_exit(1)

    return opsom_gb



def setup_tmp_dir(out_dir):
    """Creates the temporary directory
    """

    tmp_dir = os.sep.join([out_dir, 'tmp'])
    try:
        os.mkdir(tmp_dir)
    except OSError as e:
        if e.errno != EEXIST:
            print('Failed to create the temporary directory:\n' + tmp_dir + '\n' + str(e), file=stderr)
            sys_exit(1)
    
    return tmp_dir



def setup_out_dir(out_dir):
    """Creates the output directory
    """

    try:
        os.makedirs(out_dir)
    except OSError as e:
        if e.errno == EEXIST:
            print('Old files might get replaced in the already existing output directory:\n' + out_dir + '\n', file=stderr)
        else:
            print('Failed to create the output directory:\n' + out_dir + '\n' + str(e), file=stderr)
            sys_exit(1)
    
    return out_dir



def setup_version(spark_exe, scheduler):
    """Gets the SPARK version to use
    """

    version = ''
    if os.path.isdir(spark_exe):
        version += 'matlab'
    else:
        version += 'singularity'

    if scheduler != 'NONE':
        version += '+scheduler'
    
    return version



def check_iargs_integrity(iargs):
    """Integrity of the input arguments
    """

    # fMRI data
    fmri_data = [x[-1] for x in iargs['fmri_data']]
    if any(not os.path.isfile(x) for x in fmri_data):
        print('--fmri-data\n' +
              'One file does not exist or is not valid:\n' + str(fmri_data), file=stderr)
        sys_exit(1)
    elif any(not (x.endswith('.mnc') or x.endswith('.nii')) for x in fmri_data):
        print('--fmri-data\n' +
              'One file is not MINC (.mnc) or NIfTI (.nii):\n' + str(fmri_data), file=stderr)
        sys_exit(1)

    # Grey-matter mask
    if not os.path.isfile(iargs['mask']):
        print('--mask\n' +
              'Invalid or nonexistent file:\n' + iargs['mask'], file=stderr)
        sys_exit(1)
    elif not (iargs['mask'].endswith('.mnc') or iargs['mask'].endswith('.nii')):
        print('--mask\n' +
              'File is not MINC (.mnc) or NIfTI (.nii):\n' + iargs['mask'], file=stderr)
        sys_exit(1)
        
    # SPARK executable
    if not os.path.isfile(iargs['spark_exe']) and not os.path.isdir(iargs['spark_exe']):
        print('--spark-exe\n' +
              'Invalid or nonexistent file/directory:\n' + iargs['spark_exe'], file=stderr)
        sys_exit(1)
        
    # Command template
    if not os.path.isfile(iargs['cmd_template']):
        print('--cmd-template\n' +
              'Invalid or nonexistent file:\n' + iargs['cmd_template'], file=stderr)
        sys_exit(1)

    # Number of resamplings
    if iargs['nb_resamplings'] < 2:
        print('--nb-resamplings\n' +
              'Number of resamplings smaller than 2:\n' + str(iargs['nb_resamplings']), file=stderr)
        sys_exit(1)

    # Network scales
    if any(x < 1 for x in iargs['network_scales']):
        print('--network-scales\n' +
              'One element: [begin] [step] [end], is smaller than 1:\n' + str(iargs['network_scales']), file=stderr)
        sys_exit(1)
    elif iargs['network_scales'][2] < iargs['network_scales'][0]:
        print('--network-scales\n' +
              '[begin] is greather than [end]:\n' + str(iargs['network_scales']), file=stderr)
        sys_exit(1)

    # Number of iterations
    if iargs['nb_iterations'] < 2:
        print('--nb-iterations\n' +
              'Number of iterations smaller than 2:\n' + str(iargs['nb_iterations']), file=stderr)
        sys_exit(1)

    # P-value
    if (iargs['p_value'] < 0 or iargs['p_value'] > 1):
        print('--p-value\n' +
              'P-value not between 0 and 1:\n' + str(iargs['p_value']), file=stderr)
        sys_exit(1)
    
    # Block window length
    if any(x < 1 for x in iargs['block_window_length']):
        print('--block-window-length\n' +
              'One element: [begin] [step] [end], is smaller than 1:\n' + str(iargs['block_window_length']), file=stderr)
        sys_exit(1)
    elif iargs['block_window_length'][2] < iargs['block_window_length'][0]:
        print('--block-window-length\n' +
              '[begin] is greather than [end]:\n' + str(iargs['block_window_length']), file=stderr)
        sys_exit(1)

    # Maximum number of parallel jobs
    if iargs['max_parallel_jobs'] < 1:
        print('--max-parallel-jobs\n' +
              'Maximum number of parallel jobs smaller than 1:\n' + str(iargs['max_parallel_jobs']), file=stderr)
        sys_exit(1)
        
    # PSOM configuration file
    if iargs['psom_gb'] and not os.path.isfile(iargs['psom_gb']):
        print('--psom-gb\n' +
              'Invalid or nonexistent file:\n' + iargs['psom_gb'], file=stderr)
        sys_exit(1)

    return None



def setup_abspath(iargs):
    """Makes sure all paths are absolute.
    """
    
    for (i, data) in enumerate(iargs['fmri_data']):
        iargs['fmri_data'][i][-1] = os.path.abspath(data[-1])
    iargs['mask'] = os.path.abspath(iargs['mask'])
    iargs['out_dir'] = os.path.abspath(iargs['out_dir'])
    iargs['spark_exe'] = os.path.abspath(iargs['spark_exe'])
    iargs['cmd_template'] = os.path.abspath(iargs['cmd_template'])
    if iargs['psom_gb']:
        iargs['psom_gb'] = os.path.abspath(iargs['psom_gb'])
    
    return iargs



def setup_fmri_data(idata):
    """Checks the format subject/session/run from the provided data
    """

    # 1 data
    if len(idata) == 4:
        return [idata]
    elif len(idata) < 4:
        print('--fmri-data\n' + 'Invalid format, expected at least 4 elements:\n' + 
              '[subjectid sessionid runid path]\n\n' + str(idata), file=stderr)
        sys_exit(1)

    # >=1 data
    sep = [i for (i, s) in enumerate(idata) if s == ','] + [len(idata)]
    d = [b - a for (a, b) in zip([-1] + sep, sep)]
    
    if all([x == 5 for x in d]):
        odata = [[idata[i-4], idata[i-3], idata[i-2], idata[i-1]] for i in sep]
    else:
        print('--fmri-data\n' +
              'Invalid format:', file=stderr)
        for (k, i) in enumerate(sep):
            print('\n\nDATA [' + str(k+1) + ']\n', file=stderr)
            if d[k] == 5:
                print('subjectid = ' + idata[i-4] + '\nsessionid = ' + idata[i-3] +
                      '\nrunid = ' + idata[i-2] +'\npath = ' + idata[i-1], file=stderr)
            else:
                print('Expected 4 elements as:\n' + '[subjectid sessionid runid path]\n' +
                      'but received ' + str(d[k] - 1) + ':\n' + '\n'.join(idata[i - d[k] + 1:i]), file=stderr)
        sys_exit(1)

    return odata



def check_iargs_parser(iargs):
    """Defines the possible arguments of the program, generates help and usage messages,
    and issues errors in case of invalid arguments.
    """
    
    parser = ArgumentParser(
        description=dedent('''\
        SParsity-based Analysis of Reliable K-hubness (SPARK) for brain fMRI functional
        connectivity
        ____________________________________________________________________________________
         
           8b    d8 88   88 88     888888 88     888888 88   88 88b 88 88  dP 88 8b    d8
           88b  d88 88   88 88       88   88     88__   88   88 88Yb88 88odP  88 88b  d88
           88YbdP88 Y8   8P 88  .o   88   88     88""   Y8   8P 88 Y88 88"Yb  88 88YbdP88
           88 YY 88 `YbodP' 88ood8   88   88     88     `YbodP' 88  Y8 88  Yb 88 88 YY 88
           ------------------------------------------------------------------------------
                              Multimodal Functional Imaging Laboratory
        ____________________________________________________________________________________
         
        '''),
        add_help=False,
        formatter_class=RawTextHelpFormatter)

    # Required
    required = parser.add_argument_group(
        title='  REQUIRED arguments', 
        description=dedent('''\
        __________________________________________________________________________________
        '''))
    required.add_argument('--fmri-data', nargs='+', type=str,
                          required=True,
                          help=dedent('''\
                          The fMRI data to analyze.
                           
                          The data is specified as follows (see example below):
                          'subject_id session_id run_id path'.
                          subject_id, session_id and run_id begin with a letter and
                          are alphanumeric strings, and path can be absolute or
                          relative.
                          To seperate data, insert ' , ' (see example below).
                          Don't forget the simple whitespace before and after the
                          comma.
                           
                          Example:
                          sb1 ss1 run1 path_1_1_1.nii , sb1 ss2 run1 path_1_2_1.mnc
                           
                          (file formats: MINC, NIfTI)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar='XXX',
                          dest='fmri_data')
    required.add_argument('--mask', nargs=1, type=str,
                          required=True,
                          help=dedent('''\
                          Path (absolute or relative) to the grey-matter mask.
                           
                          (file formats: MINC, NIfTI)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar=('XXX'),
                          dest='mask')
    required.add_argument('--out-dir', nargs=1, type=str,
                          required=True,
                          help=dedent('''\
                          Path (absolute or relative) to the output directory.
                           
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar=('XXX'),
                          dest='out_dir')
    required.add_argument('--spark-exe', nargs=1, type=str,
                          required=True,
                          help=dedent('''\
                          Path (absolute or relative) to the SPARK Singularity image
                          or the SPARK MATLAB library (with all dependencies) to use.
                           
                          To set the image/library permanently, specify the option
                          'DEFAULT_SPARK_EXE' in the file 'DEFAULT-CONF' (set with
                          --default-conf).
                          But if you choose to do so, do not specify again --spark-exe
                          by command line for it would take precedence.
                           
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar='XXX',
                          dest='spark_exe')
    required.add_argument('--cmd-template', nargs=1, type=str,
                          required=True,
                          help=dedent('''\
                          Path (absolute or relative) to the command template file for
                          executing Singularity or MATLAB.
                           
                          To set the template file permanently, specify the option
                          'DEFAULT_CMD_TEMPLATE' in the file 'DEFAULT-CONF' (set with
                          --default-conf).
                          But if you choose to do so, do not specify again
                          --cmd-template by command line for it would take precedence.
                           
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar='XXX',
                          dest='cmd_template')

    # Optional
    optional = parser.add_argument_group(
        title='  OPTIONAL arguments',
        description=dedent('''\
        __________________________________________________________________________________
        '''))
    optional.add_argument('-h', '--help',
                          action='help',
                          help=dedent('''\
                          Shows this help message and exits.
                          ____________________________________________________________
                          '''))
    optional.add_argument('--nb-resamplings', nargs=1, type=int,
                          default=100,
                          help=dedent('''\
                          Number of bootstrap resamplings at the individual level.
                           
                          (valid values: %(metavar)s>=2)
                          (default: %(default)s)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar=('X'),
                          dest='nb_resamplings')
    optional.add_argument('--network-scales', nargs=3, type=int,
                          default=[10, 2, 30], # The display below is hacked, sorry
                          help=dedent('''\
                          Three integers, respectively: [begin] [step] [end], used to
                          create a regularly-spaced vector. In order to specify a
                          single number, for instance '12', enter the same number for
                          [begin] and [end], as: 12 1 12.
                          The numbers in the vector correspond to the range of network
                          scales to be tested. An optimal network scale will be
                          automatically estimated from the vector.
                           
                          (valid values: %(metavar)s>=1)
                          (default: 10 2 30)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar=('X'),
                          dest='network_scales')
    optional.add_argument('--nb-iterations', nargs=1, type=int,
                          default=20,
                          help=dedent('''\
                          Number of iterations for the sparse dictionary learning.
                           
                          (valid values: %(metavar)s>=2)
                          (default: %(default)s)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar=('X'),
                          dest='nb_iterations')
    optional.add_argument('--p-value', nargs=1, type=float,
                          default=0.01,
                          help=dedent('''\
                          Significance level, using a Z-test, for removing
                          inconsistent elements in the average sparse coefficients
                          (considered as the Gaussian noise) after spatial clustering.
                           
                          (valid values: 0<=%(metavar)s<=1)
                          (default: %(default)s)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar=('X'),
                          dest='p_value')
    optional.add_argument('--resampling-method', nargs=1, type=str,
                          choices=['CBB', 'AR1B', 'AR1G'],
                          default='CBB',
                          help=dedent('''\
                          Method (from NIAK) used to resample the data under the null
                          hypothesis.
                           
                          Note: If 'CBB' is selected, the option --block-window-length
                          is used.
                           
                          - CBB: Circular-block-bootstrap sample of multiple time
                          series.
                          - AR1B: Bootstrap sample of multiple time series based on a
                          semiparametric scheme mixing an auto-regressive temporal
                          model and i.i.d. bootstrap of the "innovations".
                          - AR1G: Bootstrap sample of multiple time series based on a
                          parametric model of Gaussian data with arbitrary spatial
                          correlations and first-order auto-regressive temporal
                          correlations.
                           
                          (valid values: %(choices)s)
                          (default: %(default)s)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar='X',
                          dest='resampling_method')
    optional.add_argument('--block-window-length', nargs=3, type=int,
                          default=[10, 1, 30], # The display below is hacked, sorry
                          help=dedent('''\
                          Three numbers, respectively: [begin] [step] [end], used to
                          create a regularly-spaced vector. In order to specify a
                          single number, for instance '12', enter the same number for
                          [begin] and [end], as: 12 1 12.
                          A number in the vector corresponds to a window length used
                          in the circular block bootstrap. The unit of the window
                          length is ‘time-point’ with each time-point indicating a 3D
                          scan at each TR. If the vector contains multiple numbers,
                          then a number will be randomly selected from it at each
                          resampling.
                           
                          It is recommended to use window lengths greater or equal to
                          sqrt(T), where T is the total number of time points in the
                          fMRI time-course. It is also recommended to randomize the
                          window length used at each resampling to reduce a bias by
                          window size.
                           
                          (valid values: %(metavar)s>=1)
                          (default: 10 1 30)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar='X',
                          dest='block_window_length')
    optional.add_argument('--dict-init-method', nargs=1, type=str,
                          choices=['GivenMatrix', 'DataElements'],
                          default='GivenMatrix',
                          help=dedent('''\
                          If 'GivenMatrix' is selected, then the dictionary will be
                          initialized by a random permutation of the raw data obtained
                          in step 1.
                          If 'DataElements' is selected, then the dictionary will be
                          initialized by the first N (number of atoms) columns in the
                          raw data obtained in step 1.
                           
                          (valid values: %(choices)s)
                          (default: %(default)s)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar='X',
                          dest='dict_init_method')
    optional.add_argument('--sparse-coding-method', nargs=1, type=str, 
                          choices=['OMP', 'Thresholding'], 
                          default='Thresholding',
                          help=dedent('''\
                          Sparse coding method for the sparse dictionary learning.
                           
                          (valid values: %(choices)s)
                          (default: %(default)s)
                          (type: %(type)s)
                          ____________________________________________________________
                          '''),
                          metavar='X',
                          dest='sparse_coding_method')
    optional.add_argument('--preserve-dc-atom',
                          action='store_true',
                          help=dedent('''\
                          If set, then the first atom will be set to a constant and
                          will never change, while all the other atoms will be trained
                          and updated.
                           
                          (default: %(default)s)
                          ____________________________________________________________
                          '''),
                          dest='preserve_dc_atom')
    optional.add_argument('-v', '--verbose',
                          action='store_true',
                          help=dedent('''\
                          If set, the program will provide some additional details.
                           
                          (default: %(default)s)
                          ____________________________________________________________
                          '''),
                          dest='verbose')

    # Machine configuration
    machine_conf = parser.add_argument_group(
        title='  MACHINE CONFIGURATION arguments',
        description=dedent('''\
        __________________________________________________________________________________
        '''))
    machine_conf.add_argument('--scheduler', nargs=1, type=str,
                              default='NONE',
                              choices=['NONE', 'SGE', 'SLURM', 'TORQUE'],
                              help=dedent('''\
                              Scheduler to use. If 'NONE' is chosen, then all jobs will be
                              executed in a single machine.
                               
                              To set the scheduler permanently, specify the option
                              'DEFAULT_SCHEDULER' in the file 'DEFAULT-CONF' (set with
                              --default-conf).
                              But if you choose to do so, do not specify again --scheduler
                              by command line for it would take precedence.
                               
                              (valid values: %(choices)s)
                              (default: %(default)s)
                              (type: %(type)s)
                              ____________________________________________________________
                              '''),
                              metavar='X',
                              dest='scheduler')
    machine_conf.add_argument('-i', '--interactive',
                              action='store_true',
                              help=dedent('''\
                              If set, the pipeline jobs controller will run as an
                              interactive job, allowing to monitor and control the
                              pipeline execution. Use the option --jobs-ctrl-spec to
                              set the specifications of the controller to the scheduler.

                              Note:
                              - The scheduler (--scheduler) must not be 'NONE'.
                              - No need to start an interactive session, the program will
                              automatically start one.
                               
                              To set this flag permanently, specify the option
                              'DEFAULT_INTERACTIVE' in the file 'DEFAULT-CONF' (set with
                              --default-conf).
                              But if you choose to do so, do not specify again
                              --interactive by command line for it would take
                              precedence.
                               
                              (default: %(default)s)
                              ____________________________________________________________
                              '''),
                              dest='interactive')
    machine_conf.add_argument('--jobs-ctrl-spec', nargs=1, type=str,
                              default='',
                              help=dedent('''\
                              Jobs controller specifications to the scheduler (these
                              specifications apply to only the pipeline jobs controller,
                              check --jobs-spec for configuring the jobs themselves).
                              
                              The specifications should be placed between double quotation
                              marks when using this command line as for instance:
                              "-l walltime=24:00:00 -l mem=1024" for PBS/Torque, or
                              "--time=24:00:00 --mem-per-cpu=1G" for Slurm.
                              Make sure to set a wall time at least equal to the one of
                              the jobs (if any).
                               
                              To set the specifications permanently, specify the option
                              'DEFAULT_JOBS_MANAGER_SPEC' in the file 'DEFAULT-CONF' (set
                              with --default-conf).
                              But if you choose to do so, do not specify again
                              --jobs-manager-spec by command line for it would take
                              precedence.
                               
                              (default: %(default)s)
                              (type: %(type)s)
                              ____________________________________________________________
                              '''),
                              metavar='X',
                              dest='jobs_ctrl_spec')
    machine_conf.add_argument('--jobs-spec', nargs=1, type=str,
                              default='',
                              help=dedent('''\
                              Jobs specifications to the scheduler (these specifications
                              apply to only the pipeline jobs, check --jobs-ctrl-spec for
                              configuring the jobs controller).
                               
                              The specifications should be placed between double quotation
                              marks when using this command line as for instance:
                              "-l walltime=24:00:00 -l mem=4096" for PBS/Torque, or
                              "--time=24:00:00 --mem-per-cpu=4G" for Slurm.

                              Note: environment variables from the submission environment
                              are by default propagated to the launched application.

                              To set the specifications permanently, specify the option
                              'DEFAULT_JOBS_SPEC' in the file 'DEFAULT-CONF' (set with
                              --default-conf).
                              But if you choose to do so, do not specify again --jobs-spec
                              by command line for it would take precedence.
                               
                              Alternatively, the specifications can be set permanently by
                              using the command line option --psom-gb-conf with a file.
                              In the file 'PSOM-GB', specify 'gb_psom_qsub_options = '.
                              But if you choose to do so, do not specify --jobs-spec by
                              command line, and do not specify 'DEFAULT_JOBS_SPEC' in the
                              file 'DEFAULT-CONF'. Also, make sure to propagate
                              environment variables.

                              (default: %(default)s)
                              (type: %(type)s)
                              ____________________________________________________________
                              '''),
                              metavar='X',
                              dest='jobs_spec')
    machine_conf.add_argument('--max-parallel-jobs', nargs=1, type=int,
                              default=12,
                              help=dedent('''\
                              Number of jobs to run in parallel.
                               
                              (valid values: %(metavar)s>=1)
                              (default: %(default)s)
                              (type: %(type)s)
                              ____________________________________________________________
                              '''),
                              metavar='X',
                              dest='max_parallel_jobs')

    # Expert
    expert = parser.add_argument_group(
        title='  EXPERT arguments', 
        description=dedent('''\
        For expert users. Use at your own risk.
        __________________________________________________________________________________
        '''))
    expert.add_argument('--psom-gb', nargs=1, type=str,
                        default='',
                        help=dedent('''\
                        Path (absolute or relative) to the file for configuring the
                        PSOM global variables.
                        The PSOM global variables defined in the file 'PSOM-GB' will
                        overwrite the ones in psom_gb_vars.m. Alternatively,
                        certain variables defined in the file 'PSOM-GB' can be
                        overwritten by some arguments specified by command line (see
                        Notes below).
                         
                        To set the file 'PSOM-GB' permanently, specify the option
                        'DEFAULT_PSOM_GB' in the file 'DEFAULT-CONF' (set with
                        --default-conf).
                        But if you choose to do so, do not specify again --psom-gb
                        by command line for it would take precedence.
                         
                        Notes:
                        - Setting the variable 'gb_psom_qsub_options' in the file
                        'PSOM-GB' can be overwritten if --jobs-spec is specified
                        (refer to help above).
                        - Setting the variable 'gb_psom_max_queued' in the file
                        'PSOM-GB' is definitely ignored. Use --max-parallel-jobs
                        instead (see help above).
                        - Do not mess with other variables in the file 'PSOM-GB'
                        unless you know what you are doing.
                         
                        (default: %(default)s)
                        (type: %(type)s)
                        ____________________________________________________________
                        '''),
                        metavar='XXX',
                        dest='psom_gb')
    expert.add_argument('--default-conf', nargs=1, type=str,
                        default='',
                        help=dedent('''\
                        Path (absolute or relative) to the file for configuring some
                        default options. Using this configuration file helps to
                        keep the main scripts light.
                         
                        Refer to the above command line options for a list of
                        accepted options.
                         
                        By setting any of the accepted options, no need to specify
                        the corresponding option by command line. If an option is
                        set both in this file 'DEFAULT-CONF' and by command line,
                        then the command line argument takes precedence.
                         
                        Please check the provided templates for illustration.
                         
                        (default: %(default)s)
                        (type: %(type)s)
                        ____________________________________________________________
                        '''),
                        metavar='XXX',
                        dest='default_conf')
    
    oargs = vars(parser.parse_args(iargs))

    # Hack: when (nargs=1) a list should not be returned
    for k in [
        'mask', 'out_dir', 'spark_exe', 'cmd_template',
        'nb_resamplings', 'nb_iterations', 'p_value',
        'resampling_method', 'dict_init_method', 'sparse_coding_method', 'preserve_dc_atom', 'verbose',
        'scheduler', 'interactive', 'jobs_ctrl_spec', 'jobs_spec', 'max_parallel_jobs',
        'psom_gb']:
        if type(oargs[k]) is list:
            oargs[k] = oargs[k][0]

    return oargs



def check_iargs(iargs):
    """Checks the integrity of the input arguments and returns the options if successful
    """
    
    oargs = check_iargs_parser(iargs)
    oargs['fmri_data'] = setup_fmri_data(oargs['fmri_data'])
    oargs = setup_abspath(oargs)
    check_iargs_integrity(oargs)
    oargs['version'] = setup_version(oargs['spark_exe'], oargs['scheduler'])
    return oargs



def default_cmd(iargs):
    """Checks the integrity of the app default configuration file (if any) and
    returns the corresponding command line if successful
    """
    
    cmd = []

    # Help requested, no need to go further
    if '-h' in iargs or '--help' in iargs:
        return cmd

    i = [i for (i, s) in enumerate(iargs) if s == '--default-conf']
    if len(i) == 0:
        return cmd

    default_conf = os.path.abspath(iargs[i[-1]+1])
    if not os.path.isfile(default_conf):
        print('The default configuration file is invalid or nonexistent:\n' + default_conf, file=stderr)
        sys_exit(1)

    default_args = [
        'DEFAULT_SPARK_EXE', 
        'DEFAULT_CMD_TEMPLATE', 
        'DEFAULT_SCHEDULER', 
        'DEFAULT_INTERACTIVE', 
        'DEFAULT_JOBS_CTRL_SPEC', 
        'DEFAULT_JOBS_SPEC', 
        'DEFAULT_PSOM_GB'
        ]
    with open(default_conf, 'r', newline='\n') as file:
        for line in file:
            for args in default_args:
                if line.startswith(args + ' '):
                    cmd += ['--' + args.replace('DEFAULT_', '').replace('_', '-').lower(),
                            line.partition(args + ' ')[2][:-1]] # [:-1] to ignore EOL
                    break

    return [x for x in cmd if x != '']



def main(iargs):
    """Main function, checks the inputs, makes the necessary files to run SPARK
    """

    oargs = check_iargs(default_cmd(iargs) + iargs)

    setup_out_dir(oargs['out_dir'])
    
    tmp_dir = setup_tmp_dir(oargs['out_dir'])

    oargs['psom_gb'] = setup_psom_gb(oargs['psom_gb'], oargs['version'], oargs['spark_exe'], oargs['scheduler'],
                                     oargs['jobs_spec'], oargs['max_parallel_jobs'], tmp_dir)

    pipe_opt = setup_pipe_opt(oargs, tmp_dir)

    app_spec = setup_app_spec(oargs, tmp_dir)

    main_job = setup_main_job(oargs['version'], oargs['cmd_template'], oargs['spark_exe'], oargs['scheduler'], pipe_opt, app_spec, tmp_dir)
    
    entrypoint_opt = setup_entrypoint_opt(main_job, oargs['interactive'], oargs['scheduler'], oargs['jobs_ctrl_spec'], tmp_dir)

    print(entrypoint_opt)

    return sys_exit(0)



############## Main
if __name__ == "__main__":
    main(argv[1:])
    