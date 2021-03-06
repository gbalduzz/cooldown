import os
import math

algorithm = "DCA+"  # "DCA+"|"DCA"

##################################################################
# Parameters
d = 2.00
period = 2
global_seed = 0

temps = [1,  0.5,  0.25, 0.1, 0.05, 0.025, .01]
T_start_analysis = 0.25  # Starting temperature for computing two-particle quantities and doing the analysis.


channel = "PARTICLE_PARTICLE_UP_DOWN"
qvec = [0, 0]

sigma_cutoff = 0.5
radius_cutoff = 1.5

# pysics parameters
U=4
Nc=9
##################################################################

def my_format(x):
    return ("%.6g" % x)

def prepare_input_file(filename, T, input_data = "zero"):
    file = open(filename, "r")
    text = file.read()
    file.close()

    text = text.replace("ALGORITHM", algorithm)
    
    text = text.replace("INPUT_DATA", input_data)
    text = text.replace("TEMP", str(T))
        
    text = text.replace("BETA", str(my_format(1./T)))
    text = text.replace("DENS", str(d))

    global global_seed
    text = text.replace("SEED", str(global_seed))
    global_seed += 1
        
    if (T >= 1.0):
        text = text.replace("ITERS", "8")
    else:
        text = text.replace("ITERS", "3")

    #text = text.replace("VECX", str(vecx))
    #text = text.replace("VECY", str(vecy))

    text = text.replace("PERIOD", str(period))


    text = text.replace("CHANNEL", channel)
    text = text.replace("QVEC", str(qvec))
    text = text.replace("SIGMACUTOFF", str(sigma_cutoff))
    text = text.replace("RADIUSCUTOFF", str(radius_cutoff))

    file = open(filename, "w")
    file.write(text)
    file.close()


dca_batch_str = ''
analysis_batch_str = ''
srun_str = 'srun -n $SLURM_NTASKS  -c $SLURM_CPUS_PER_TASK '

input_data = 'zero'
for T in temps:
    print my_format(T)
    dirname = "./T_" + str(T)
    if (not os.path.exists(dirname)):
        cmd = "mkdir " + dirname
        os.system(cmd)

    input_tp = dirname + "/input_tp.json"
    input_sp = dirname + "/input.sp.json"

    data_dca_sp   = dirname + "/data."+algorithm+"_sp.hdf5"
    data_dca_tp   = dirname + "/data."+algorithm+"_tp.hdf5"
    data_analysis = dirname + "/data.BSE.hdf5"

    section = "dca"
    # dca sp
    if (not os.path.exists(data_dca_sp)):
        cmd = "cp ./input.sp.json.in " + input_sp
        os.system(cmd)
        prepare_input_file(input_sp, T, input_data)
        input_data = data_dca_sp

        outname = dirname + "/out.sp.txt"
        dca_batch_str += "echo \"start sp T = " + str(T) + "  $(date)\" \n"
        dca_batch_str += srun_str + " ./main_dca " + input_sp + " > " + outname + "\n"

    # dca tp
    do_tp = 0
    if (T<=T_start_analysis and not os.path.exists(data_dca_tp)):
        do_tp = 1
        cmd = "cp ./input.tp.json.in " + input_tp
        os.system(cmd)
        prepare_input_file(input_tp, T, input_data)
        input_data = data_dca_tp

        outname = dirname + "/out.tp.txt"
        dca_batch_str += "echo \"start tp T = " + str(T) + "  $(date)\" \n"
        dca_batch_str += srun_str + " ./main_dca " + input_tp + " > " + outname + "\n"

    # analysis
    section = "analysis"
    if (do_tp and not os.path.exists(data_analysis)):
        outname = dirname + "/out.analysis.txt"
        analysis_batch_str +=  srun_str + " ./main_analysis " + input_tp + " > " + outname + "\n"


job_names = ["dca", "analysis"]
for name in job_names:
    file = open("job."+ name +".slm.in", "r")
    text = file.read()
    file.close()
    
    batch_script_name = "job.fe_as."+ name + "_"+algorithm+".slm"
    batch_str = dca_batch_str if name == "dca" else analysis_batch_str
        
    text = text.replace("DENS", str(d))
    text = text.replace("SIZE", str(Nc))
    text = text.replace("ALGORITHM", algorithm)
    text = text.replace("JOBS", batch_str)

    file = open(batch_script_name, "w")
    file.write(text)
    file.close()
