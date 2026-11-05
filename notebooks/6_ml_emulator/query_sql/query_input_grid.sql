select 
   ds.path as ds_path
   , ds.name as ds_name
   , ds."fileFormat" as ds_format
   , ds.type as ds_type
   , ds.description as ds_description
   , ds."spatialCoverage" as ds_spatial_coverage
from datasets as ds
where
   ds.type = 'global_input' 
and
   --ds.name = 'C_CT.grd'
   ds.name = %(name_grd)s