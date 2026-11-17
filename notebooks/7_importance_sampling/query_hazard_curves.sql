---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select Simulation Runs Parameters of scenarios for a given manning coefficient
--    Input: 
--       - manning_coef: value of Manning Coefficient to select
--    Output: 
--       - SImulation Runs parameters of scenarios: averate rate, magnitude, lon, lat, max ts and arrival time
---------------------------------------------------------------------------------------------------------------------------------




with sr_params as (
	select 
		fk_sr_id,
		seismicity_type,
		magnitude,
		COALESCE(fault_centre_lon,mesh_fault_bc_lon) as lon,
		COALESCE(fault_centre_lat,mesh_fault_bc_lat) as lat,
		list_rates as rates
	from parameters_v1
	where
		manning_coeff = %(manning_coef)s
),
sr_params_ext as (
select 
	sr.id as sr_id,
	sr.name as id_scen,
	sr_params.seismicity_type,
	sr_params.magnitude,
	sr_params.lon,
	sr_params.lat,
	sr_params.rates
from sr_params
inner join simulations as sr
	on sr_params.fk_sr_id = sr.id
)
select
	sr_params_ext.*,
	ds.path as path_nc_file
from sr_params_ext
inner join rel_sr_ds as rel
	on sr_params_ext.sr_id= rel.fk_sr_id
inner join datasets as ds
	on rel.fk_ds_id = ds.id
where
	ds.name = CONCAT('C_','%(site_loc)s', '.nc')