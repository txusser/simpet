scanner =	{
  #Model Name
  "name": "GE_Discovery",
  "brand": "General Electric",
  "model": "Discovery STE",
  #Parameters for Phantom Preparation
  "STIR_target_size": [2,2,1.308],
  #Cylindrical PET Parameters
  "Ring_Number": 24,
  "Ring_Z_thickness": 0.63,
  "Gap_between_rings": 0.08,
  "Ring_Inner_Radious": 44.32,
  "Ring_Outer_Radious": 47.32,
  "SimSET_Ring_Material": 18,
  "Energy_Resolution_percent": 16, 
  "Timing_Resolution_ns": False,
  #Reconstruction
  "Max_Ring_Diff": 23,
  "Ring_Detectors": 560,
  "Tangential_Bins": 293,
  "recons_zoomFactor": 1.23,
  "recons_xyOutputSize": 128,      
  "recons_zOutputSize": 47,	       
  "recons_numberOfSubsets": 7,     
  "recons_numberOfIterations": 42,
  "recons_savingInterval": 4,
  "TOF_reconstruction": False,
  "LM_reconstruction": False
}