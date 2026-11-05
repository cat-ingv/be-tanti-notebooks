---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select bathymetry grid files
---------------------------------------------------------------------------------------------------------------------------------


-- select bathymetry grid files
select 
	split_part(ds.name, '.', 1) as site,
	ds.path as path_bathy_file
from datasets as ds
where
   ds.fk_exp_id='exp_ct_sr'
and
	ds.type = 'global_input'
and
	ds.name in ('C_CT.grd','C_SR.grd')