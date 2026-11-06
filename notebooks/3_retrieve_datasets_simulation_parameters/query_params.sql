---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select Simulation Runs Parameters 
--    Input: 
--    Output: 
--       - List of all Simulation Run parameters for each scenario
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
sr_params as (
	select
      -- general parameters
		params.fk_sr_id,
		params.seismicity_type,
		params.magnitude,
		params.manning_coeff,
      -- bs parameters
		params.fault_centre_lon,
		params.fault_centre_lat,
		params.fault_centre_depth,
		params.fault_length,
		params.fault_width,
		params.strike,
		params.dip,
		params.rake,
		params.slip as slip,
      -- ps parameters (avg)
		params.mesh_fault_bc_lon,
      params.mesh_fault_bc_lat,
      params.mesh_fault_rake_uniform,
      params.mesh_fault_slip_avg,
      -- output parameters
      max_ts_ct,
      max_ts_sr,
      arrival_time_ct/60 as arrival_time_min_ct,
      arrival_time_sr/60 as arrival_time_min_sr
      --GREATEST(params.max_ts_ct,params.max_ts_sr) as max_ts
	from parameters_v1 as params
   limit 500000
)
select 
   sr_exp.*,
   sr_params.*
from sr_exp
inner join sr_params
   on sr_exp.sr_id=sr_params.fk_sr_id