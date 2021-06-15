import arcpy
import datetime as dt

gdb = r"C:\Users\come.daval\Documents\ArcGIS\Projects\Sentinel_20\Sentinel_20.gdb"
couche = "Fusion_Data"
ChampIDFusion = "ID_Fusion_90j"
date_field = "date_date"
NumS = "Num_S"
fields = [ChampIDFusion, NumS, date_field]
annee_etude = 2020
dbt_etude = dt.datetime(annee_etude, 1, 1)

arcpy.MakeFeatureLayer_management(gdb + "/" + couche, couche)
liste_id_fusion = [list(l) for l in arcpy.da.SearchCursor(couche, fields, where_clause=ChampIDFusion + " = " + NumS)]
print(len(liste_id_fusion))

liste_a_supp = []
for feu_ref in liste_id_fusion:
    if feu_ref[2] < dbt_etude:
        liste_a_supp.append(feu_ref[0])
print(len(liste_a_supp))
try:
    arcpy.AddField_management(couche, "A_SUPPRIMER", "TEXT", field_length=255)
except:
    arcpy.DeleteField_management(couche, "A_SUPPRIMER")
    arcpy.AddField_management(couche, "A_SUPPRIMER", "TEXT", field_length=255)
fields.append("A_SUPPRIMER")
uCurs = arcpy.da.UpdateCursor(couche, fields)
for u in uCurs:
    if u[0] in liste_a_supp:
        u[3] = "A SUPPRIMER"
        uCurs.updateRow(u)

wc = "A_SUPPRIMER IS NULL AND Nature <> 'G' AND Nature <> 'V' AND Nature <> 'D'"
arcpy.MakeFeatureLayer_management(couche, couche + "_propre", where_clause=wc)
arcpy.DeleteField_management(couche + "_propre", "A_SUPPRIMER")
arcpy.CopyFeatures_management(couche + "_propre", gdb + "/" + couche + "_propre")

arcpy.Delete_management(couche + "_propre")