from methodes import calcul_indice_confiance
import arcpy

couche = "Fusion_Data_1"
gdb = r"C:\Users\come.daval\Documents\ArcGIS\Projects\GDB_HUGO\GDB_HUGO.gdb"
date_field = "date_date"
seuil_t = 90
seuil_s = 0.6
calcul_indice_confiance(gdb, couche, date_field, seuil_t, seuil_s)