---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select Simulation Runs Outputs based on Simulation Runs Parameters 
--    Input: 
--       - mag_min,mag_max: min and max value of magnitudo to select
--       - manning_coef_min,manning_coef_max: min and max value of Manning Coefficient to selected_sr
--       - fault_length_min,fault_length_max: min and max value of the fault lenght
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
sr_params as (
	select
      -- general parameters
		params.fk_sr_id,
		params.seismicity_type,
		params.magnitude,
		params.manning_coeff,
      coalesce(params.slip,params.mesh_fault_slip_avg) as slip_bs_ps,
      coalesce(params.rake,params.mesh_fault_rake_uniform) as rake_bs_ps,
		-- bs parameters
      params.fault_centre_lon,
		params.fault_centre_lat,
		params.fault_centre_depth,
		params.fault_length,
		params.fault_width,
		params.strike,
		params.dip,
      -- ps parameters
      params.mesh_fault_bc_lon,
      params.mesh_fault_bc_lat,
		params.mesh_fault_bbox
	from parameters_v1 as params
   limit 500000
),
-- select srs wrt filter on params
selected_sr as (
   select 
      sr_exp.sr_id,
      sr_exp.sr_path,
      sr_exp.scen_name,
      sr_params.*
   from sr_exp
   inner join sr_params
      on sr_exp.sr_id=sr_params.fk_sr_id
   where
      -- check magnitude is in an interval
      --magnitude between 6 and 9
      magnitude between %(mag_min)s and %(mag_max)s
   and
      -- check manning coefficient is in an interval 
      --manning_coeff between 0 and 0.03
      manning_coeff between %(manning_min)s and %(manning_max)s
   and 
      -- check strike is in an interval
      --(strike is null or strike between 60 and 70)
      (strike is null or strike between %(strike_min)s and %(strike_max)s)
   and 
      -- check dip is in an interval
      --(dip is null or dip between 50 and 60)
      (dip is null or dip between %(dip_min)s and %(dip_max)s)
   and
      -- check rake is in an interval
      --(rake_bs_ps between 60 and 300)
      (rake_bs_ps between %(rake_min)s and %(rake_max)s)
   and
      -- check slip is in an interval
      --(slip_bs_ps between 0 and 10)
      (slip_bs_ps between %(slip_min)s and %(slip_max)s)
   and
      -- check fault_length is in an interval
      -- (fault_length is null or fault_length between 0 and 200)
      (fault_length is null or fault_length between %(fault_length_min)s and %(fault_length_max)s)
   and
      -- check fault_width is in an interval
      --(fault_width is null or fault_width between 0 and 200)
      (fault_width is null or fault_width between %(fault_width_min)s and %(fault_width_max)s)
   and
   --      -- bbox: '{15.9,36.,14.6,16.,36.3,15.1}'
   --      -- rake: 60-300 
   --      -- slip: 0-10)
      (check_point_in_3dbbox(fault_centre_lon,fault_centre_lat,fault_centre_depth,%(ev_bbox)s)
       or
       intersect_3Dbboxes(mesh_fault_bbox,%(ev_bbox)s)
      )
),
selected_output as (
   select 
      _ds.path as ds_path
      , _ds.name as ds_name
      , _sr.*
   from selected_sr as _sr
   inner join rel_sr_ds as _rel
      on _sr.sr_id=_rel.fk_sr_id
   inner join datasets as _ds
      on _rel.fk_ds_id=_ds.id
   where
      _ds.name in ('C_CT.nc','C_SR.nc')
   and
      intersect_2Dbboxes(_ds."spatialCoverage",%(area_bbox)s)
)
select * from selected_output;