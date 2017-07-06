########################################
# Python 3.6
# Coding: utf-8
# DK: Dette script henter automatisk Geodanmark data fra kortforsyningen FTP, pakker det ud
# og importerer det ind i en given Postgis setting.
# Author: Hans Skaarup Larsen
# Contact: Hemd12@gmail.com
# 2017/07/05
#README:
# Remember to set Username/Password/Areanumber/BBOX in lines 23-28 and
# Set the Postgres connection settings and schema for OGR2OGR in line 86.
# The schema must also be manually created from the
#Credits:
########################################

import ftplib
import traceback, sys
import os
import zipfile
import glob
import datetime
import shutil

#Folder containing the python script
init_folder =  os.path.dirname(os.path.realpath(__file__))
Output_folder =  init_folder + os.sep + "Data_Folder"
#Kortforsyningen username and password
Username = "INSERT USERNAME"
Password = "INSERT PASSWORD"
#Number used to to identify .Zip file from kortforsyningen FTP. 1085 covers Most of Zealand?
Areanumber = FOUR DIGIT AREANUMBER
#Set bounding box used in ogr2ogr xmin ymin xmax ymax
bbox =  "BBOX SEPERATED BY SPACES"

#Function that retrieves geodanmark data
def retrieve_geodanmark_data(Outputfolder):
    try:
        ftp = ftplib.FTP('ftp.kortforsyningen.dk', Username, Password)
        ftp.cwd('grundlaeggende_landkortdata/fot/SHAPE')
        filename = str(Areanumber) + "_SHAPE_UTM32-EUREF89.zip"
        file = open(Outputfolder + os.sep + filename, 'wb')
        ftp.retrbinary('RETR ' + filename, file.write)
        file.close
        ftp.close
        print (filename)
    #Expection message
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        print (tbinfo + "\n" + str(sys.exc_info()[0])+ ": " + str(sys.exc_info()[1]))

# Creates output_folder if it does not exist - then runs function above
try:
    if not os.path.exists(Output_folder):
        os.makedirs(Output_folder)
    retrieve_geodanmark_data(Output_folder)
#Exception message
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = tbinfo + "\n" + str(sys.exc_info()[0])+ ": " + str(sys.exc_info()[1])
    #
    print (pymsg)

#Unzip file and organize for OGR2OGR import
zip_files = glob.glob(os.path.dirname(os.path.realpath(__file__)) + os.sep + "Data_Folder" + os.sep + '*.zip')
print (zip_files)
for zip_filename in zip_files:
    zip_dir = os.path.splitext(zip_filename)[0]
    file_name = os.path.split(zip_dir)[1]
    print(zip_dir)
    file_nr = file_name[:5]
    zip_handler = zipfile.ZipFile(zip_filename, "r")
#Unpacks the Zip file conaining all Geodanmark data.
    zip_handler.extractall(zip_dir)
    zip_handler.close()

#Finds all shapefiles in the unpack directory KORT10/ADM and GEO folders.
#shp_dir = zip_dir + os.sep + file_name + os.sep + "FOT"
    shp_files = glob.glob(zip_dir + os.sep + file_name + os.sep + "FOT" + os.sep + "*" + os.sep + "*.shp")
#shp_files.extend(glob.glob(shp_dir + os.sep + "GEO" + os.sep + "*" + os.sep + "*.shp"))

#Prepare Shapefile Names
    file_name = []
    for i in range(len(shp_files)):
        file_name.append(str(shp_files[i].rsplit('\\', 1)[-1])[:-4])

#OGR2OGR to Postgis
#OGR2OGR iterartion based on number of shape files in shp_files list and file_name
for n in range(len(shp_files)):
    encoding_command = "set pgclientencoding=utf-8"
    ogr2ogr = "ogr2ogr -overwrite -f \"PostgreSQL\" PG:\"host=HOST port=PORT dbname=DATABASE user=USER password=PASSWORD\" " + shp_files[n] + " -nln SCHEMA." + str(file_name[n])  + " -spat " + bbox + " -a_srs \"EPSG:25832\" "
    os.system(encoding_command + ' & ' + ogr2ogr)

#Writes update date to logfile
last_update_f = init_folder + os.sep + 'Update_log.txt'
last_update = open(last_update_f, 'a')
last_update.writelines("\nOpdateret: " + datetime.datetime.now().date().isoformat())
last_update.close

#Cleanup: removes downloaded zip_file and unpacked data
shutil.rmtree(Output_folder, ignore_errors=False, onerror=None);
