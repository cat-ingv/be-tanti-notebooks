----------------------------------------------------------------------
-- QUERY: Visualize Simulation Runs for the given experiment
--    Input: 
--       - num_srs: number of simulation runs to visualize
--    Output: 
--       - selected srs (including datasets) for the given experiment
----------------------------------------------------------------------

-- select srs for the given experiment
with exp_srs as (
   select 
      _sr.fk_exp_id as exp_id
      , _sr.id as sr_id
      , _sr.name as sr_name
   from simulations as _sr
   where
      _sr.fk_exp_id='exp_ct_sr'
   limit %(num_srs)s
),
-- select datasets for each simulation run of the experiment
exp_sr_ds as (
   select 
      exp_srs.*
      , _ds.path as ds_path
      , _ds.name as ds_name
      , _ds.type as ds_type
   from exp_srs
   inner join rel_sr_ds as _rel
      on exp_srs.sr_id=_rel.fk_sr_id
   inner join datasets as _ds
      on _rel.fk_ds_id=_ds.id
),
-- select global input datasets to each simulation run of the experiment
exp_ds as (
   select 
      exp_srs.*
      , _ds.path as ds_path
      , _ds.name as ds_name
      , _ds.type as ds_type
   from exp_srs
   inner join datasets as _ds
      on exp_srs.exp_id=_ds.fk_exp_id
   where
      _ds.fk_exp_id is not null
)
select * 
from exp_sr_ds
union all
select * 
from exp_ds