---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select Simulation Runs Outputs based on Simulation Runs Parameters 
--    Input: 
--       - mag_min,mag_max: min and max value of magnitudo to select
--       - manning_coef_min,manning_coef_max: min and max value of Manning Coefficient to selected_sr
--       - fault_lenght_min,fault_lenght_max: min and max value of the fault lenght
--       - fault_width_min,fault_width_max: min and max value of the fault width
--       - rake_min,rake_max: min and max value of rake to select
--       - slip_min,slip_max: min and max value of slip to select
--       - strike_min,strike_min: min and max value of strike to select (for BS-events)
--       - dip_min,dip_max: min and max value of dip to select (for BS-events)
--       - in_bbox: 3D bounding box where to search epicenter of the BS-events or the centroid of the mesh faults for PS-event 
--    Output: 
--       - selected Simulation Runs Output
---------------------------------------------------------------------------------------------------------------------------------



-- select simulation runs for the given experiment
with sr_exp as (
select
   id as sr_id
   , path as sr_path
   , name as scen_name
from simulations
where
   fk_exp_id='exp_ct_sr'
),
-- associate to each simulation runs its parameters: mag,manning, (lon,lat,depth,strike,dip,rake)/(mesh)
sr_params_ps as (
	select
      -- general parameters
		params.fk_sr_id,
		params.seismicity_type,
		params.magnitude,
		params.manning_coeff,
      -- ps parameters
		params.mesh_fault_bc_lon,
      params.mesh_fault_bc_lat,
      params.mesh_fault_rake_uniform,
      params.mesh_fault_slip_avg,
      ST_AsText(params.mesh_fault) as mesh_fault,
      mesh_fault_slip_distr as mesh_slip
	from parameters_v1 as params
   where
      params.seismicity_type = 'PS'
   and
      params.manning_coeff = 0.01
   limit 500000
)
select 
   sr_exp.*,
   sr_params_ps.*
from sr_exp
inner join sr_params_ps
   on sr_exp.sr_id=sr_params_ps.fk_sr_id