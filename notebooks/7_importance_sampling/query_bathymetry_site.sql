---------------------------------------------------------------------------------------------------------------------------------
-- QUERY: Select bathymetry grid file for a given site
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
	ds.name = CONCAT('C_','%(site_loc)s', '.grd')