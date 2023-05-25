#!/usr/bin/env python

from yaml import safe_load, load, dump
from netCDF4 import Dataset
import numpy as np
from scipy.io import FortranFile
import argparse

def parse_args():
   p = argparse.ArgumentParser(description='Convert binary to netcdf restart')
   p.add_argument('-i','--input',type=str,help='input binary',default=None)
   p.add_argument('-o','--output',type=str,help='output netcdf',default=None)
   p.add_argument('-d','--dscr',type=str,help='descriptor file',default=None)
   p.add_argument('-t','--hdr',type=bool,help='file has header',default=False)
   p.add_argument('-p','--prec',type=str,help='float or double',default='float')
   p.add_argument('--debug',action='store_true',help='turn on debug prints')
   return vars(p.parse_args())

def writeCVars(coordVars,dimensions):

   for v in coordVars:
       if v=='time':
          coordVars[v][:]=0
       elif (v=='lat') | (v=='lon') | (v=='lev') | (v=='edges'):
          dsize=dimensions[v]
          coords=np.arange(1,dsize+1)
          coordVars[v][:]=coords

def writeVar(v, vars, dimensions, bintype):
   var=vars[v['short_name']]
   dims = v['dimension']
   # is tile?
   if 'tile' in dims:
      if ('subtile' in dims) & (len(dims)==2):
         rec=f.read_reals(dtype=bintype)
         tilesize=dimensions.get('tile')
         for i in range(dimensions.get('subtile')):
             var[i,:]=rec[i*tilesize:(i+1)*tilesize]
      elif (len(dims)==2) & ( ('unknown_dim1' in dims) | ('unknown_dim2' in dims) ):
         if 'unknown_dim1' in dims:
            dsize=dimensions.get('unknown_dim1')
         if 'unknown_dim2' in dims:
            dsize=dimensions.get('unknown_dim2')
         for i in range(dsize):
            rec = f.read_reals(dtype=bintype)
            var[i,:]=rec
      elif (len(dims)==3) & ('unknown_dim1' in dims) & ('unknown_dim2' in dims):
         for j in range(dimensions.get('unknown_dim2')):
            for i in range(dimensions.get('unknown_dim1')):
               rec = f.read_reals(dtype=bintype)
               var[j,i,:]=rec
      elif (len(dims)==1):
         rec = f.read_reals(dtype=bintype)
         var[:]=rec

   # is gridded
   elif 'lat' in dims:
      if 'lev' in dims:
         for i in range(dimensions.get('lev')):
            rec = f.read_reals(dtype=bintype)
            var[i,:,:]=rec
      elif 'edges' in dims:
         for i in range(dimensions.get('edges')):
            rec = f.read_reals(dtype=bintype)
            var[i,:,:]=rec
      else:
         rec = f.read_reals(dtype=bintype)
         var[:,:]=rec
   # is just lev
   else:
      if 'edges' in dims:
         rec = f.read_reals(dtype=bintype)
         var[:]=rec

def defineDimVars(fid,dims):
   coordVars = {}
   for d in dims:
       if d=="lon":
          newVar=fid.createVariable(d,'f8',d)
          setattr(newVar,'units','degrees_east')
          setattr(newVar,'long_name','Longitude')
          coordVars.update([(d,newVar)])
       if d=="lat":
          newVar=fid.createVariable(d,'f8',d)
          setattr(newVar,'units','degrees_north')
          setattr(newVar,'long_name','Latitude')
          coordVars.update([(d,newVar)])
       if d=="lev":
          newVar=fid.createVariable(d,'f8',d)
          setattr(newVar,'units','layer')
          setattr(newVar,'long_name','sigma_at_layer_midpoints')
          setattr(newVar,'standard_name','atmosphere_hybrid_sigma_pressure_coordinate')
          setattr(newVar,'coordinate','eta')
          setattr(newVar,'positive','down')
          setattr(newVar,'formulaTerms','ap: ak b: bk ps: ps p0: p00')
          coordVars.update([(d,newVar)])
       if d=="edges":
          newVar=fid.createVariable(d,'f8',d)
          setattr(newVar,'units','level')
          setattr(newVar,'long_name','sigma_at_layer edges')
          setattr(newVar,'standard_name','atmosphere_hybrid_sigma_pressure_coordinate')
          setattr(newVar,'coordinate','eta')
          setattr(newVar,'positive','down')
          setattr(newVar,'formulaTerms','ap: ak b: bk ps: ps p0: p00')
          coordVars.update([(d,newVar)])
       if d=="time":
          newVar=fid.createVariable(d,'f8',d)
          setattr(newVar,'units','minutes since ')
          setattr(newVar,'long_name','time')
          coordVars.update([(d,newVar)])

   return coordVars

comm_args = parse_args()
file = comm_args['dscr']
binfile = comm_args['input']
ncfile = comm_args['output']
sdtype = comm_args['prec']
hdr = comm_args['hdr']
debug = comm_args['debug']

if (sdtype=='float'):
   bintype=np.float32
elif (sdtype=='double'):
   bintype=np.float64


f=open(file,'r')

data=safe_load(f)

dimensions = data["dimensions"]
variables = data["variables"]

if debug:
   print(dump(variables))
   print(dump(dimensions))



ncfid = Dataset(ncfile,mode='w',format='NETCDF4')

dimids = {}
for d in dimensions:
    dsize = dimensions.get(d)
    newDim = ncfid.createDimension(d,dsize)
    dimids.update([(d,newDim)])

cVars = defineDimVars(ncfid,dimids)
    
vars = {}
for v in variables:
    sname = v['short_name']
    lname = v['long_name']
    units = v['units']
    dims = v['dimension']
    newVar = ncfid.createVariable(sname,'f4',dims)
    setattr(newVar,'long_name',lname)
    setattr(newVar,'units',units)
    vars.update([(sname,newVar)])

writeCVars(cVars,dimensions)

f=FortranFile(binfile,'r')
if hdr:
   if debug:
      print("reading header")
   rec = f.read_ints(dtype=np.int32)
   if debug:
      print(rec)
   rec = f.read_ints(dtype=np.int32)  
   if debug:
      print(rec)

for v in variables:
   writeVar(v,vars,dimensions,bintype)

ncfid.close()

