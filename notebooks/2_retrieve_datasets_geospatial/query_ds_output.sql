----------------------------------------------------------------------
-- QUERY: Select output Data Products based on geospatial information
--    Input: 
--       - in_bbox: bounding box where to search data products datasets
--    Output: 
--       - metadata selected data products
----------------------------------------------------------------------

select 
   ds.path as ds_path
   , ds.name as ds_name
   , ds."fileFormat" as ds_format
   , ds.type as ds_type
   , ds.description as ds_description
   , ds."spatialCoverage" as ds_spatial_coverage
from datasets as ds
where
   ds."fileFormat" = 'nc'
and
   ds.type = 'output'
and
	--intersect_2Dbboxes(ds."spatialCoverage",'{15.2,37.0,15.35,37.2}')=true
   intersect_2Dbboxes(ds."spatialCoverage",%(in_bbox)s)=true;
