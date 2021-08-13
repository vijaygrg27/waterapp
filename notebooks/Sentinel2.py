#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ee
import geemap
import geemap.colormaps as cm
import warnings
warnings.filterwarnings("ignore")

Map = geemap.Map()
Map.add_basemap('HYBRID')


def maskS2clouds(image):
  qa = image.select('QA60')

#  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11

#  # Both flags should be set to zero, indicating clear conditions.
  mask = qa.bitwiseAnd(cloudBitMask).eq(0)       .And(qa.bitwiseAnd(cirrusBitMask).eq(0))

  return image.updateMask(mask).divide(10000)

geometry= ee.Geometry.Polygon([[76.79911551271984,30.6168475776271],
                            [76.79911551271984,30.62644958134403],
                            [76.78280768190929,30.62644958134403],
                            [76.78280768190929,30.6168475776271]])

S2_SR = ee.ImageCollection('COPERNICUS/S2_SR')

S2_SR = ee.ImageCollection('COPERNICUS/S2_SR').filterBounds(geometry)

Map.centerObject(geometry)

S2_SR = ee.ImageCollection('COPERNICUS/S2_SR').filterBounds(geometry)        .filterDate('2021-01-01', '2021-08-06')        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',20))                   .map(maskS2clouds)        .select(['B8','B4','B11'])

def addNDVI(image):
  ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
  return image.addBands(ndvi)

def addNDMI(image):
  ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')
  return image.addBands(ndmi)

S2_SR = S2_SR.map(addNDMI)
S2_SR= S2_SR.map(addNDVI)

# Convert the image collection to an image.
#image= S2_SR.toBands()
image= S2_SR.select('NDVI').toBands()
image1= S2_SR.select('NDMI').toBands()
recent_S2 = ee.Image(S2_SR.sort('system:time_start', False).first())

print('Recent image: ', recent_S2)

palette = cm.palettes.ndvi

NDVIpalette=palette

#NDVIpalette = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901', '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']

ndviVis = {
  'min': 0.0,
  'max': 1.0,
  'palette': palette
   }


ndmiVis = {
  'min': 0.0,
  'max': 1.0,
  'palette': palette
   }
# Center the map

ndvi=recent_S2.select('NDVI')
ndmi=recent_S2.select('NDMI')

Map.setCenter(76.8006, 30.6238, 14)

Map.addLayer(image,{}, 'Timeseries of Sentinel NDVI',opacity=.1)
Map.addLayer(image1,{}, 'Timeseries of Sentinel NDMI',opacity=.1)
# Time-series marker
Map.set_plot_options(add_marker_cluster=False,position='bottomright',overlay=True,max_height=250,max_width=800)
#Map.addLayer(recent_S2.select('NDVI'), ndviVis, 'Recent Sentinel NDVI')
#Map.addLayer(recent_S2.select('NDMI'), ndviVis, 'Recent Sentinel NDMI')
Map


# In[2]:


# To Draw features on a particular layer
roi1 = ee.FeatureCollection(Map.draw_features)
ndvi_img=ndvi.clip(roi1)
Map.addLayer(ndvi_img,ndviVis,'NDVI_image')
ndmi_img=ndmi.clip(roi1)
Map.addLayer(ndmi_img,ndmiVis,'NDMI_image')

