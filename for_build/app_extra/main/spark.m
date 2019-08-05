function spark(varargin)
try
    %% Parsing scheme
    valid_fields = {...
        'fmri_data'; 'mask'; 'out_dir'; ...
        'nb_resamplings'; 'network_scales'; 'nb_iterations'; 'p_value'; ...
        'resampling_method'; 'block_window_length'; 'dict_init_method'; ...
        'sparse_coding_method'; 'preserve_dc_atom'; ...
        'verbose'; 'psom_gb'};
    
    p = struct();
    [fid, msg] = fopen(varargin{1}, 'r');
    if fid == -1
        fprintf('\n     - Could not open the options file:\n%s', msg);
        exit(1)
    end
    
    while true
        s = fgetl(fid);
        if ((numel(s) == 1) && (s == -1))
            break
        end
        
        k = strfind(s, ' ');
        if isempty(k)
            continue
        end
        
        kk = find(strcmp(valid_fields, s(1:k(1)-1)), 1);
        
        if ~isempty(kk)
            p.(valid_fields{kk}) = s(k(1)+1:end);
        end
    end
    fclose(fid);
    
    if str2double(p.verbose)
        fprintf('\n\n     ***** \nUsing the following public parameters:\n')
        disp(p)
        fprintf('\n     ***** \n\n')
    end
    
    
    %% Private parameters below (for now...)
    p.rerun_step1 = '0';
    p.rerun_step2 = '0';
    p.rerun_step3 = '0';
    p.rerun_step4 = '0';
    p.sparsity_level = '';
    p.network_scale = '';
    p.error_flag = '0';
    p.display_progress = '1';
    p.session_flag = '1';
    % p.out_size = 'quality_control'; % useless...
    p.test = '0';
    
    % Be safe, some code may forget to append filesep...
    p.out_dir = [p.out_dir, filesep];
    
    
    %% Creates the options structure to run SPARK
    opt = struct();
    
    % Subjects
    data = strsplit(p.fmri_data, ' , ');
    for k = 1:numel(data)
        sep = strfind(data{k}, ' ');
        files_in.(data{k}(1:sep(1)-1)).fmri.(data{k}(sep(1)+1:sep(2)-1)).(data{k}(sep(2)+1:sep(3)-1)) = data{k}(sep(3)+1:end);
    end
    clear data k sep
    
    
    % Step 1: Bootstrap resampling
    opt.folder_tseries_boot.mask = p.mask;
    opt.folder_tseries_boot.nb_samps = str2double(p.nb_resamplings);
    opt.folder_tseries_boot.bootstrap.dgp = p.resampling_method;
    opt.folder_tseries_boot.bootstrap.block_length = str2RegSpacedVector(p.block_window_length);
    opt.folder_tseries_boot.flag = str2double(p.rerun_step1);
    
    
    % Step 2: sparse dictionary learning
    opt.folder_kmdl = opt.folder_tseries_boot;
    opt.folder_kmdl.flag = str2double(p.rerun_step2);
    opt.folder_kmdl.ksvd.param = struct(...
        'test_scale', str2RegSpacedVector(p.network_scales), ...
        'numIteration', str2double(p.nb_iterations), ...
        'errorFlag', str2double(p.error_flag), ...
        'preserveDCAtom', str2double(p.preserve_dc_atom), ...
        'InitializationMethod', p.dict_init_method, ...
        'SparsecodingMethod', p.sparse_coding_method, ...
        'displayProgress', str2double(p.display_progress)...
        );
    if isempty(p.sparsity_level)
        opt.folder_kmdl.ksvd.param.L = [];
    end
    if isempty(p.network_scale)
        opt.folder_kmdl.ksvd.param.K = [];
    end
    
    
    % Step 3: spatial clustering
    opt.folder_global_dictionary = opt.folder_kmdl;
    opt.folder_global_dictionary.flag = str2double(p.rerun_step3);
    
    
    % Step 4: k-hubness map generation
    opt.folder_kmap.nb_samps = opt.folder_tseries_boot.nb_samps;
    opt.folder_kmap.ksvd = opt.folder_kmdl.ksvd;
    opt.folder_kmap.pvalue = str2double(p.p_value);
    opt.folder_kmap.flag = str2double(p.rerun_step4);
    
    
    % Miscellaneous
    opt.flag_session = str2double(p.session_flag);
    opt.folder_in = ''; % useless...
    opt.folder_out = p.out_dir;
    % opt.size_output = p.out_size; % useless...
    opt.flag_test = str2double(p.test);
    
    
    % PSOM options, see psom_gb_vars_local
    prependFileToFile(which('spark_psom_gb.m'), p.psom_gb);
    addpath(genpath(fileparts(p.psom_gb)));
    
    
    %% Runs SPARK
    [pipeline, opt] = spark_pipeline_fmri_kmap(files_in, opt); %#ok
    save([p.out_dir, filesep, 'pipeline', '.mat'], 'pipeline', 'opt')

    fprintf('\n\n\n     - To terminate the program, type ''exit''\n');
catch err
    fprintf(['     - An exception occured:\n', err.message]);
    exit(1)
end
end