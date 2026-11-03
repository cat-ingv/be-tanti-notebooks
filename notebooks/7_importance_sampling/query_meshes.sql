---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select Simulation Runs Parameters of scenarios for a given manning coefficient
--    Input: 
--       - manning_coef: value of Manning Coefficient to select
--    Output: 
--       - SImulation Runs parameters of scenarios: averate rate, magnitude, lon, lat, max ts and arrival time
---------------------------------------------------------------------------------------------------------------------------------




with sr_mesh as (
	select 
		params.fk_sr_id,
		params.seismicity_type,
  		ST_AsText(params.mesh_fault) as mesh_fault
	from parameters_v1 as params
	where
		manning_coeff = %(manning_coef)s
	and
		seismicity_type= 'PS'
)
select * from sr_mesh