----------------------------------------------------------------------
-- QUERY: Select output Data Products based on geospatial information
--    Input: 
--       - in_bbox: bounding box where to search data products datasets
--    Output: 
--       - metadata selected data products
----------------------------------------------------------------------


with ds_sel as (
	select 
		sim.name as sim_name,
		ds.name as ds_name,
		ds.path as ds_path,
		ds."spatialCoverage" as ds_coverage,
		params.seismicity_type,
		params.manning_coeff,
		params.max_ts_ct,
		params.max_ts_sr
	from datasets as ds
	inner join rel_sr_ds as rel
		on ds.id = rel.fk_ds_id
	inner join simulations as sim
		on sim.id=rel.fk_sr_id
	inner join parameters_v1 as params
		on params.fk_sr_id = sim.id
	where
		ds.shared=false
	and
		ds.type='output'
	and
		--params.manning_coeff=0.01
		params.manning_coeff=%(manning_value)s
	and
		--intersect_2dbboxes(ds."spatialCoverage",'{15.0,37.2,15.15,37.6}')=true
		--intersect_2dbboxes(ds."spatialCoverage",'{15.2,37.0,15.35,37.2}')=true
		intersect_2dbboxes(ds."spatialCoverage",%(in_bbox)s)=true
)
select 
	ds_sel.sim_name
	, MAX(CASE WHEN ds_sel.ds_name in ('C_CT.nc','C_SR.nc') THEN ds_sel.ds_path END) as C_nc
	, MAX(CASE WHEN ds_sel.ds_name in ('C_CT.nc','C_SR.nc') THEN ds_sel.ds_coverage END) as ds_coverage
	, MAX(CASE WHEN ds_sel.ds_name = 'grid0_ts.nc' THEN ds_sel.ds_path END) AS grid0_ts
	, MAX(seismicity_type) AS seismicity_type
	, MAX(manning_coeff) AS manning_coeff
	, CASE WHEN MIN(ds_sel.ds_name) = 'C_CT.nc' THEN MAX(max_ts_ct) 
    	   WHEN MIN(ds_sel.ds_name) = 'C_SR.nc' THEN MAX(max_ts_sr) 
	  END AS max_ts
from ds_sel
group by ds_sel.sim_name

