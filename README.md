# GEOS5_restart_converter
Converts GEOS-5 binary to NetCDF restarts
This can be used to convert a set of MERRA2 restarts via a script like this, the utility must be run for each different restart:
```
./bin2nc.py -i fvcore_internal_rst -o fvcore_internal_rst.nc4 -d fv.yaml -p double -t True
./bin2nc.py -i moist_internal_rst -o moist_internal_rst.nc4 -d moist.yaml
./bin2nc.py -i pchem_internal_rst -o pchem_internal_rst.nc4 -d pchem.yaml
./bin2nc.py -i landice_internal_rst -o landice_internal_rst.nc4 -d landice.yaml
./bin2nc.py -i lake_internal_rst -o lake_internal_rst.nc4 -d lake.yaml
./bin2nc.py -i saltwater_internal_rst -o saltwater_internal_rst.nc4 -d salt.yaml
./bin2nc.py -i catch_internal_rst -o catch_internal_rst.nc4 -d catch.yaml
```
