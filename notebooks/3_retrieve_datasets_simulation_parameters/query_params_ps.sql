---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select Simulation Runs Parameters for PS-type scenarios for a given value of manning coefficiet (0.01)
--    Input: 
--    Output: 
--       - List of Simulation Run parameters for each PS-type scenario
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