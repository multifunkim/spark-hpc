#!/bin/bash
# 
# Runs SPARK Singularity version (frame meant to be used by spark_setup.py)
# 
# Last revision: August, 2019
# Maintainer: Obai Bin Ka'b Ali @aliobaibk
# License: In the app folder or check GNU GPL-3.0.



VAR_INS ### THIS SHOULD BE THE FIRST COMMAND, DO NOT EDIT



if [[ "$scheduler" == "SLURM" ]]; then
    cmd_job_sub="sbatch --job-name="
    cmd_job_stat="sstat --format=JobID -j"
    cmd_job_del="scancel"

elif [[ "$scheduler" == "SGE" ]] || [[ "$scheduler" == "TORQUE" ]]; then
    cmd_job_sub="qsub -N " # don't forget to add a simple whitespace at the end
    cmd_job_stat="qstat -j"
    cmd_job_del="qdel"

fi



############## Cleaning function
clean () {
    echo -e "\n\n\n     ***** Doing some cleaning, PLEASE WAIT"
    
    kill -9 $manager_id >/dev/null 2>&1
    
    # Submitted jobs
    #echo -e "\n     - Deleting submitted jobs..."
    while read jobid; do
        if [[ "$jobid" =~ ^[0-9]+$ ]]; then
            $cmd_job_stat "$jobid" &>/dev/null
            if [[ $? == 0 ]]; then $cmd_job_del "$jobid"; fi
        fi
    done < "$jobs_log"
    
    # Temporary directory
    #echo -e "\n     - Deleting temporary files..."
    #rm -rf "$tmp_dir" >/dev/null 2>&1
    rm -rf "$tmp_dir"/fifo* >/dev/null 2>&1
    rm -rf "$tmp_dir"/job-* >/dev/null 2>&1
    
    echo -e "\n     - All cleanings done, the program will close"
    echo -e "\n     BYE\n"
}
if [[ $scheduler != 'NONE' ]]; then
    trap clean EXIT
fi



############## Function creating the jobs to be submitted from a FIFO
jobs_manager () {
    while true; do
        if read line; then
            jobopt=(${line%"SPLIT_LINE singularity_exec_options"*})
            if [[ ${jobopt[0]} == "qsub_options" ]]; then
                sopt=(${line##*"SPLIT_LINE singularity_exec_options"})

                job="$(mktemp "$tmp_dir/job-XXXXX.bash")"
                echo -e '#!/bin/bash\n''singularity exec -B "'"$sing_binds"'" -H "'"$sing_home"'"':'"'"$sing_home"'" '"${sopt[@]}" > "$job"
                chmod u+x "$job"

                jobid="$($cmd_job_sub"${jobopt[@]:2}" "$job")"
                echo $(echo "$jobid" | awk 'match($0,/[0-9]+/){print substr($0, RSTART, RLENGTH)}') >> "$jobs_log"
            else
                echo -e "\n     - Ignoring a value read from the FIFO:\n""$line"
            fi
        fi
    done < "$fifo"
}



############## Main
if [[ $scheduler != 'NONE' ]]; then
    jobs_manager >/dev/null 2>&1 &
    manager_id=$!
fi


