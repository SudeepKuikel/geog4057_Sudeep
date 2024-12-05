import arcpy
import os
import ee
import pandas as pd


"""Code for reading CSV and changing it to feature class. Importing DEM and then extracting elevation of each point of feature class from elevation data"""
def getGeeElevation(workspace,csv_file,outfc_name,epsg=4326):
    """Workspace:Directory that contains input and output
        CSV file: input csv file name
        epsg: WKID of the spatial reference you want to use"""
    
    #Load the CSV file
    csv_file=os.path.join(workspace,csv_file)
    #csv_file="boundary.csv"#Replace with your file
    data=pd.read_csv(csv_file) 
    dem=ee.Image('USGS/3DEP/10m')
    print(epsg)
    geometrys=[ee.Geometry.Point([x,y],f'EPSG:{epsg}') for x,y in zip(data['X'], data['Y'])]
    fc=ee.FeatureCollection(geometrys)
    origin_info=fc.getInfo()
    sampled_fc=dem.sampleRegions(collection=fc,scale=10,geometries=True)
    sampled_info=sampled_fc.getInfo()
    for ind, itm in enumerate(origin_info['features']):
        itm['properties']=sampled_info['features'][ind]['properties']
    
    
    fcname=os.path.join(workspace,outfc_name)
    if arcpy.Exists(fcname):
        arcpy.management.Delete(fcname)
    arcpy.management.CreateFeatureclass(workspace,outfc_name,geometry_type='POINT',spatial_reference=32119)
    arcpy.management.AddField(fcname,field_name='elevation',field_type='FLOAT')
    
    with arcpy.da.InsertCursor(fcname,['SHAPE@','elevation']) as cursor:
        for feat in origin_info['features']:
            #get the coordinates and create a point geometry
            coords=feat['geometry']['coordinates']
            pnt=arcpy.PointGeometry(arcpy.Point(coords[0],coords[1]),spatial_reference=32119)
            #get the properties and write it to the 'elevation'
            elev=feat['properties']['elevation']
            cursor.insertRow([pnt,elev])




def main():
    import sys
    try:
        ee.Initialize()
    except:
        ee.Authenticate()
        ee.Initialize()
        
    workspace=sys.argv[1]
    csv_file=sys.argv[2]
    outfc_name=sys.argv[3]
    epsg=int(sys.argv[4])
    getGeeElevation(workspace=r'S:\projectGEOG4057\workspace',csv_file='boundary.csv',outfc_name='pnt_elev1',epsg=32119)

if __name__=='__main__':
    
    
    main()
    
 
 
 
 
    

