import os
from os.path import join
import commands
import sys
import shutil
from utils import tools


class STIR_Simulation(object):
    def __init__(
        self,
        scanner,
        simpet_dir,
        simulation_name,
        results_name,
        act_map,
        att_map,
        pet_image=False,
    ):
        # Configuring inputs
        self.simulation_dir = join(simpet_dir, "Data", self.simulation_name)
        self.emiss_map = join(self.simulation_dir, "Maps", act_map)
        self.att_map = join(self.simulation_dir, "Maps", att_map)
        self.original_pet = join(self.simulation_dir, "Maps", pet_image)
        # This is the smoothing to simulate PR and NC.
        # Most reasonable value for clinical scanners is around 2 mm
        self.prnc_fwhm = 2

        # Configuring outputs
        self.results_dir = join(self.simulation_dir, "results", results_name)

        # Configuring scanner
        self.target_size = scanner.scanner_target_size
        self.scanner_template = scanner.scanner_template
        self.proyector = scanner.proyector

        # Configuring required resources
        self.stir_dir = join(simpet_dir, "include", "stir", "bin")

        # Configuring logging
        self.logfile = os.path.join(self.results_dir, "STIR_simulation.log")

    def run(self):
        """
        This function will run the whole default simulation
        """
        print("Applying Positron range and non-colinearity smoothing")
        self.positron_range_non_col_filter()

        print("Obtaining emission and attenuation projections...")
        self.create_line_integrals()

    def positron_range_non_col_filter(self, input_image):
        """
        Applies a Gaussian filter to the activity map
        """
        # This part reads the .hv file
        hdr_header = tools.anything_to_hdr_convert(input_image)
        hdr_img = hdr_header[0:-3] + "img"
        data_file = hdr_header[0:-3] + "v"

        mfile_name = join(self.results_dir, "smoothing_act.m")

        smoothed_img = tools.smoothing(
            self.matlab_rcommand,
            mfile_name,
            img_file,
            self.prnc_fwhm,
            "s",
            self.logfile,
        )

        shutil.copy(smoothed_img, data_file)

    def create_line_integrals(self):
        """
        Uses forward_project to project the activity sinograms!
        """
        rcommand = "%s/forward_project %s/my_line_integrals.hs %s %s %s" % (
            self.stir_dir,
            self.results_dir,
            self.emiss_map,
            self.scanner_template,
            self.proyector,
        )
        tools.osrun(rcommand, self.logfile)

    def calculate_attenuation_coefficients(self):
        """
        Uses forward_project to project the activity sinograms!
        """
        rcommand = (
            "%s/calculate_attenuation_coefficients --PMRT --ACF %s/my_acfs.hs %s %s"
            % (self.stir_dir, self.results_dir, self.att_map, self.scanner_template)
        )
        tools.osrun(rcommand, self.logfile)

    def apply_normalization_factors(self):
        """
        This function is meant to calculate and apply normalization factors
        """
        # right now, just use a constant sinogram
        # (all bins set to 3.4 here, just to check if it's handled properly in the script)
        rcommand = (
            "%s/stir_math -s --including-first --times-scalar 0 --add-scalar 3.4 %s/my_norm.hs %s/my_acfs.hs"
            % (self.stir_dir, self.results_dir, self.results_dir)
        )
        tools.osrun(rcommand, self.logfile)

        rcommand = (
            "%s/stir_math -s -mult %s/my_multifactors.hs %s/my_norm.hs %s/my_acfs.hs"
            % (self.stir_dir, self.results_dir, self.results_dir, self.results_dir)
        )
        tools.osrun(rcommand, self.logfile)

    def create_random_coincidences(self):
        """This will calculate randoms and add them to our coincidences"""
        # TODO compute sensible randoms-to-true background here
        rcommand = (
            "%s/stir_math -s --including-first --times-scalar 0 --add-scalar 100 %s/my_randoms.hs %s/my_line_integrals.hs"
            % (self.stir_dir, self.results_dir, self.results_dir)
        )
        tools.osrun(rcommand, self.logfile)
        # we divide by the norm here to put some efficiency pattern on the data.
        # this isn't entirely accurate as a "proper" norm contains geometric effects
        # which shouldn't be in the randoms, but this is supposed to be a "simple" simulation :-;
        rcommand = (
            "%s/stir_divide -s --accumulate --times-scalar 0 --add-scalar 100 %s/my_randoms.hs %s/my_line_integrals.hs"
            % (self.stir_dir, self.results_dir, self.results_dir)
        )

        "$DIR_STIR/stir_divide -s --accumulate $DIR_PROJECTIONS/my_randoms.hs $DIR_PROJECTIONS/my_norm.hs >> $DIR_LOGS/stir_math.log 2>> $DIR_LOGS/stir_math.errors"
