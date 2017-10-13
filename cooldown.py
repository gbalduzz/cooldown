import os
import math

section = "dca"  # "dca"|"analysis"
algorithm = "DCA+"  # "DCA+"|"DCA"

# Parameters
d = 2.00
period = 2

temps = [1,  0.5,  0.25, 0.1, 0.05, 0.025, .01]
T_start_analysis = 0.25  # Starting temperature for computing two-particle quantities and doing the analysis.


channel = "PARTICLE_PARTICLE_UP_DOWN"
qvec = [0, 0]

sigma_cutoff = 0.5
radius_cutoff = 1.5


def my_format(x):
    return ("%.6g" % x)

U=4
Nc=9
def prepare_input_file(filename, T_ind):
    file = open(filename, "r")
    text = file.read()
    file.close()

    text = text.replace("ALGORITHM", algorithm)
    
    if (T_ind == 0):
        text = text.replace("./T=PREVIOUS_TEMP/data."+algorithm+"_sp.hdf5", "zero")
    else:
        text = text.replace("PREVIOUS_TEMP", str(temps[T_ind-1]))

    text = text.replace("TEMP", str(temps[T_ind]))
        
    text = text.replace("BETA", str(my_format(1./temps[T_ind])))
    text = text.replace("DENS", str(d))

        
    if (temps[T_ind] >= 1.0):
        text = text.replace("ITERS", "8")
    else:
        text = text.replace("ITERS", "3")

#    text = text.replace("VECX", str(vecx))
 #   text = text.replace("VECY", str(vecy))

    text = text.replace("PERIOD", str(period))


    text = text.replace("CHANNEL", channel)
    text = text.replace("QVEC", str(qvec))
    text = text.replace("SIGMACUTOFF", str(sigma_cutoff))
    text = text.replace("RADIUSCUTOFF", str(radius_cutoff))

    file = open(filename, "w")
    file.write(text)
    file.close()


batch_str = ''
srun_str = 'srun -n $SLURM_NTASKS  -c $SLURM_CPUS_PER_TASK '

for T_ind, T in enumerate(temps):
    print my_format(T)
    dirname = "./T=" + str(T)
    if (not os.path.exists(dirname)):
        cmd = "mkdir " + dirname
        os.system(cmd)

    input_tp = dirname + "/input_tp.json"
    input_sp = dirname + "/input.sp.json"

    data_dca_sp   = dirname + "/data."+algorithm+"_sp.hdf5"
    data_dca_tp   = dirname + "/data."+algorithm+"_tp.hdf5"
    data_analysis = dirname + "/data.BSE.hdf5"

    # dca sp
    if (section == "dca" and not os.path.exists(data_dca_sp)):
        cmd = "cp ./input.sp.json.in " + input_sp
        os.system(cmd)
        prepare_input_file(input_sp, T_ind)
        outname = dirname + "/out.sp.txt"
        batch_str += "echo \"start sp T = " + str(T) + "  $(date)\" \n"
        batch_str = batch_str + srun_str + " ./main_dca " + input_sp + " > " + outname + "\n"

    # dca tp
    if (section == "dca" and T<=T_start_analysis and not os.path.exists(data_dca_tp)):
        cmd = "cp ./input.tp.json.in " + input_tp
        os.system(cmd)
        prepare_input_file(input_tp, T_ind)
        outname = dirname + "/out.tp.txt"
        batch_str += "echo \"start tp T = " + str(T) + "  $(date)\" \n"
        batch_str = batch_str + srun_str + " ./main_dca " + input_tp + " > " + outname + "\n"

    # analysis
    if (section == "analysis" and os.path.exists(data_dca_tp) and not os.path.exists(data_analysis)):
        outname = dirname + "/out.analysis.txt"
        batch_str = batch_str + srun_str + " ./main_analysis " + input_tp + " > " + outname + "\n"

if (section == "dca"):
    file = open("job.dca.slm.in", "r")
    text = file.read()
    file.close()
    
    batch_script_name = "job.fe_as.dca_"+algorithm+".slm"
        
elif (section == "analysis"):
    file = open("job.analysis.slm.in", "r")
    text = file.read()
    file.close()
    
    batch_script_name = "job.fe_as.analysis_"+algorithm+".slm"
    
text = text.replace("DENS", str(d))
text = text.replace("SIZE", str(Nc))
text = text.replace("ALGORITHM", algorithm)
text = text.replace("JOBS", batch_str)

file = open(batch_script_name, "w")
file.write(text)
file.close()
