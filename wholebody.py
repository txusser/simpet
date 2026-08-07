import os, yaml, sys
import shutil
import nibabel as nib
import numpy as np
from os.path import join, exists
from omegaconf import DictConfig, OmegaConf
from pyprojroot import here
from utils import tools
from utils import wb_tools

def save_cfg(cfg, path):
    with open(path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False)

sys.path.append(str(here()))
from simpet import SimPET


class WholebodySimulation(object):
    """
    This class provides functionalities to simulate several beds.
    You have to initialize the class with a params file. The class will iteratively call the SimPET class.
    Before using SimPET, check out the README.

    """

    def __init__(self, cfg: DictConfig):

        # Initialization
        self.simpet_dir = here()
        self.cfg_omega= cfg
        self.cfg = OmegaConf.to_container(cfg)
        self.params = self.cfg["params"]
        self.config = {k: v for k, v in self.cfg.items() if k != "params"}
        self.scanner = self.cfg["params"]["scanner"]
        self.scanner_model = str(self.params["scanner"]["scanner_name"]).lower().replace(" ", "_")
        self.cfg_omega.params.scanner.scanner_name = self.scanner_model

        # The following lines will read the general, scanner and config parameters
        self.sim_type = self.params.get("sim_type")
        self.zmin = float(self.params.get("z_min"))
        self.zmax = float(self.params.get("z_max"))

        # This will load the environment config
        self.cesga = self.config.get("cesga")

        if self.cesga:
            self.dir_data = self.config.get("cesga_data_path")
        else:
            self.dir_data = self.config.get("dir_data_path")
            if not self.dir_data:
                self.dir_data = join(self.simpet_dir, "Data")

        if self.cesga:
            self.dir_results = self.config.get("cesga_results_path")
        else:
            self.dir_results = self.config.get("dir_results_path")
            if not self.dir_results:
                self.dir_results = join(self.simpet_dir, "Results")
        if not exists(self.dir_results):
            os.makedirs(self.dir_results)

    def run(self):

        patient_dir = self.params.get("patient_dirname")
        act_map = join(self.dir_data, patient_dir, self.params.get("act_map"))
        att_map = join(self.dir_data, patient_dir, self.params.get("att_map"))
        output_name = self.params.get("output_dir")
        output_dir = join(self.dir_results, output_name)
        maps_dir = join(output_dir, "Maps")

        # THIS WILL POP UP EVEN IF ONLY RECONSTRUCTION IS DONE. MOVE IT OUT
        if not exists(output_dir):
            os.makedirs(output_dir)
        
        #Summary of General Parameters
        save_cfg(self.cfg, join(output_dir, f"{patient_dir}_{self.scanner_model}_wholebody.yaml"))
        
        log_file = join(output_dir, "logfile.log")
        

        beds_cs = wb_tools.calculate_center_slices(self, act_map, self.scanner, self.zmin, self.zmax)

        print("\nNumber of simulation to be performed: %s" % len(beds_cs))    #num_beds = len(beds_cs)
        print("Beds center slides: %s\n" % beds_cs)

        # Global Params
        sim_time_original_global = float(self.params.get("simulation_time", 0))
        sim_dose_original_global = float(self.params.get("total_dose", 0))
        self.apply_correction_for_NECR = self.params.get("correction_for_NECR", 0)

    
        # Apply NECR correction if enabled

        # === Correction NECR ===
        if int(self.apply_correction_for_NECR) == 1:
            print("\n>>> Applying NECR correction for this simulation...")
            print(f"Original Time of Simulation: {sim_time_original_global} seg")

            #  Calculate corrected times (one per bed)
            sim_times_per_bed, phantom_doses_FOV = wb_tools.correction_for_NECR(self, act_map, sim_time_original_global)

        else:
            print("\nNECR correction disabled _ keeping original simulation time.")
            sim_times_per_bed = [sim_time_original_global] * len(beds_cs)
            phantom_doses_FOV = [sim_dose_original_global] * len(beds_cs)


        # === Run a simulation per bed ===  
        for j, (cs, sim_time_bed, dose ) in enumerate(zip(beds_cs, sim_times_per_bed, phantom_doses_FOV), start=1):
            
            print(f"\n>>> Running simulation for bed {j} with center slice {cs}, total dose into the FOV: {dose} and time = {sim_time_bed} seg <<<")
           
            # Create folder for this bed
            bed_dir = join(output_dir, f"Bed_{j}_CenterSlice_{cs}")
            os.makedirs(bed_dir, exist_ok=True)

            # Create copy of configuration file
            cfg_copy = OmegaConf.create(OmegaConf.to_container(self.cfg_omega))
            cfg_copy.params.center_slice = int(cs)
            cfg_copy.params.simulation_time = sim_time_bed
            cfg_copy.params.output_dir = join(output_name, f"Bed_{j}_CenterSlice_{cs}")
            
            # Save the configuration for each bed
            save_cfg(OmegaConf.to_container(cfg_copy), join(bed_dir, f"{patient_dir}_{self.scanner_model}_bed{j}.yaml"))
            #  Run simulation
            bed_simu = SimPET(cfg_copy)
            bed_simu.run()

        print("\nAll simulations completed successfully.\n") 
         
        # The following line will be ralated with the simulation of each beds: 
        recons_beds = []
        recons_norm_beds = []

        recons_algorithm = self.scanner.get('recons_type')
        recons_it = self.scanner.get('numberOfIterations')

        for i, cs in enumerate(beds_cs, start=1):
            recons_dir = join(output_dir, "Bed_%s_CenterSlice_%s" % (i, cs), "%s_Sim_%s" % (self.sim_type, self.scanner_model),recons_algorithm)
            recons_file = join(recons_dir, 'rec_%s_%s.hdr' % (recons_algorithm, recons_it))
            recons_beds.append(recons_file)


        # ===  Correction for Normalization ===
        self.Normalization = self.params.get("correction_for_normalization", 0)

        if self.Normalization == 1 and len(recons_beds) > 0:
            print("\n>>> Applying NORMALIZATION correction for Reconstructed Image...")

            # Normalization factors for each bed
            factors = wb_tools.normalization_factor_correction(self)

            for i, recons_file in enumerate(recons_beds, start=1):
                if not os.path.exists(recons_file):
                    print(f"File not found: {recons_file}")
                    continue

                if i - 1 >= len(factors):
                    raise RuntimeError("Normalization factors do not match number of beds")

                print(f"\nApplying normalization correction to bed {i}: {recons_file}")   

                factor = factors[i - 1]
                print(f">>> Bed {i} normalization factor applied: {factor}")

                # Load reconstructed image
                img = nib.load(recons_file)
                data = img.get_fdata()

                # Apply normalization
                data_norm = data * factor

                # Save normalized image
                recons_dir = os.path.dirname(recons_file)
                recons_norm_file = join(recons_dir, f"rec_{recons_algorithm}_{recons_it}_norm.hdr")

                img_norm = nib.Nifti1Image(data_norm, img.affine, img.header)
                nib.save(img_norm, recons_norm_file)

                recons_norm_beds.append(recons_norm_file)
                print(f"Normalized image saved in: {recons_norm_file}")

        # === Joined Beds ===
        self.joints_beds = self.params.get("joints_beds", 0)

        # Paths for the final joined images
        joint_beds = join(output_dir, f"rec_{recons_algorithm}_{recons_it}.hdr")
        joint_norm_beds = join(output_dir, f"rec_{recons_algorithm}_{recons_it}_norm.hdr")
        
        n_beds = len(recons_beds)
        n_norm_beds = len(recons_norm_beds)
        print(f"Norm_bed = {n_norm_beds}")

        # ---------- NO JOIN (0 or single bed) ----------
        if self.joints_beds == 0 or n_beds == 1:
            print("\n>>> No bed joining required (single bed or joints_beds = 0)")

            # Copy the reconstructed image
            src_hdr = recons_beds[0]
            src_img = src_hdr.replace('.hdr', '.img')  # asociado .img
            if not os.path.exists(src_hdr) or not os.path.exists(src_img):
                raise FileNotFoundError(f"Reconstructed bed files not found: {src_hdr} / {src_img}")

            shutil.copy(src_hdr, joint_beds)
            shutil.copy(src_img, joint_beds.replace('.hdr', '.img'))
            print(f"Copied single bed image to: {joint_beds}")

            # Copy normalized image if Normalization is enabled
            if self.Normalization == 1 and n_beds == 1:
                src_norm_hdr = recons_norm_beds[0]
                src_norm_img = src_norm_hdr.replace('.hdr', '.img')
                shutil.copy(src_norm_hdr, joint_norm_beds)
                shutil.copy(src_norm_img, joint_norm_beds.replace('.hdr', '.img'))
                print(f"Copied normalized bed image to: {joint_norm_beds}")

               
        # ---------- ACTUAL JOIN more than one bed) ----------
        else:
            try:
                print("\n>>> Joining reconstructed beds...")
                wb_tools.join_beds_wb(self, act_map, recons_beds, joint_beds)
                print("Bed joining completed.")
            except Exception as e:
                print(f"Error while joining beds: {e}")

            if self.Normalization == 1 and n_beds > 1:
                try:
                    joint_norm_beds = join(output_dir, f"rec_{recons_algorithm}_{recons_it}_norm.hdr")
                    wb_tools.join_beds_wb(self, act_map, recons_norm_beds, joint_norm_beds)

                    print("Joining of normalized beds completed.")
                except Exception as e:
                    print(f"Error while joining normalized beds: {e}")


        # === Quantification ===
        self.quantification = self.params.get("quantification_info", 0) 
        joint_norm_beds = join(output_dir, f"rec_{recons_algorithm}_{recons_it}_norm.hdr") ## tratar de mencionarlo solo una vez!! #TODO

        try:
            #Copy the mask in the same orientation of the simulated image
            mask_dir = self.params.get("mask_dirname")
            mask_map = join(self.dir_data, mask_dir, self.params.get("mask_map"))

            rotated_mask_file = join(output_dir, "rotated_mask.nii")
            rotated_mask = wb_tools.rotate_and_flip_mask(act_map, mask_map, rotated_mask_file, joint_beds, self.zmin, self.zmax)
            

            #Changed the dimension of the mash to the same of the simulated image
            mask_file = join(output_dir, "mask_image.nii")
            reshaped_mask_image = wb_tools.change_act_dimensions(mask_file, rotated_mask, joint_beds)

            #Doing Quantification of Final Image
            if self.quantification == 1 and self.joints_beds == 1 and joint_norm_beds is not None: # es si existen los ficheros Arreglar!!!!

                quantification_file = join(output_dir, "Quantification_data.txt")
                info_act_map = join(output_dir, "Activity_distribution_data.txt")

                label_file_mask = join(self.dir_data, mask_dir, "mask_map.txt")
                label_file_act_map = join(self.dir_data, patient_dir, "act_map.txt")
                
                import inspect
                print(inspect.signature(wb_tools.total_quantification))
                wb_tools.total_quantification(mask_file, joint_norm_beds, quantification_file, label_file_mask)

                wb_tools.distribution_of_dose_into_phantom(self, maps_dir, act_map, info_act_map, label_file_act_map)
                
                print("Quantification finished")

        except Exception as e:
            print(f"Error: Quantification was not performed: {e}")