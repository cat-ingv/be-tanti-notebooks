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
		avg_rate,
		avg_rate / SUM(avg_rate) OVER(PARTITION BY magnitude) AS avg_rate_norm,
		list_rates as rates,
		magnitude,
		COALESCE(fault_centre_lon,mesh_fault_bc_lon) as lon,
		COALESCE(fault_centre_lat,mesh_fault_bc_lat) as lat,
		--max_ts_sr as max_ts,
		(CASE WHEN '%(site_loc)s' = 'SR' THEN max_ts_sr WHEN '%(site_loc)s' = 'CT' THEN max_ts_ct ELSE NULL END) as max_ts,
		--arrival_time_sr/60 as arrival_time_min
		(CASE WHEN '%(site_loc)s' = 'SR' THEN (arrival_time_sr/60) WHEN '%(site_loc)s' = 'CT' THEN (arrival_time_ct/60) ELSE NULL END) as arrival_time_min	
	from parameters_v1
	where
		manning_coeff = %(manning_coef)s
),
sr_params_ext as (
select 
	sr.name as id_scen,
	sr_params.seismicity_type,
	sr_params.avg_rate,
	sr_params.avg_rate_norm,
	sr_params.rates,
	sr_params.magnitude,
	sr_params.lon,
	sr_params.lat,
	sr_params.max_ts,
	sr_params.arrival_time_min
from sr_params
inner join simulations as sr
	on sr_params.fk_sr_id = sr.id
)
select * from sr_params_ext