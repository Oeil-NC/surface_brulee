import arcpy
from methodes import *
from FctArcpy import *
import datetime as dt

def creation_id_feux(ListCoucheRef, ListChampsDate, l_couches, list_nature, list_oid):
    # creation des champs  Nature et Num_S pour ne pas perdre l'origine de la couche et les identifiants avant fusion
    for i in range(len(list_nature)):
        arcpy.MakeFeatureLayer_management(l_couches[i], "couche" + list_nature[i])
        add_field_Nature_Num("couche" + list_nature[i], list_nature[i], list_oid[i])
        arcpy.Delete_management("couche" + list_nature[i])

    # MeF des champs date
    for couche, dateName in zip(ListCoucheRef, ListChampsDate):
        date_field = arcpy.ListFields(couche, "date")
        if len(date_field) > 0:
            date_f = date_field.pop()
            if date_f.type == "String":
                continue
            else:
                # arcpy.DeleteField_management(couche, date_f)
                pass
        # Nom du champ date, au format str, en sortie, défaut : date
        dateNewName = "date"
        arcpy.AddField_management(couche, dateNewName, 'String')
        try:
            arcpy.CalculateField_management(couche, dateNewName, "datetime.datetime.strftime(!"+dateName+"!, '%Y%m%d')")
        except TypeError:
            arcpy.CalculateField_management(couche, dateNewName, "!" + dateName + "!")

def creation_couche_fusionnee(datedate_field, fcSentinel, fcDSCGR, fcVIIRS, fcGS, fieldDate, Nom_sortie, where_clause, where_clause_ref, buffer):
    # Selection des polygones de l'annee d'etude (01/01/annee_etude - 31/02/annee_etude+1)
    arcpy.MakeFeatureLayer_management(fcSentinel, "coucheSentinel", where_clause=where_clause)
    # Selection des polygones de reference (01/01/annee_etude-1 - 31/02/annee_etude+1)
    arcpy.MakeFeatureLayer_management(fcDSCGR, "coucheDSCGR", where_clause=where_clause_ref)
    arcpy.MakeFeatureLayer_management(fcVIIRS, "coucheVIIRS", where_clause=where_clause_ref)
    arcpy.MakeFeatureLayer_management(fcGS, "coucheGS", where_clause=where_clause_ref)
    
    # Fusion des tables
    arcpy.Merge_management(["coucheSentinel", "coucheDSCGR", "coucheVIIRS", "coucheGS"],
                        arcpy.env.workspace + os.sep + Nom_sortie)
    arcpy.Buffer_analysis("coucheSentinel", "coucheSentinel_Buffer", buffer)
    arcpy.Merge_management(["coucheSentinel_Buffer", "coucheDSCGR", "coucheVIIRS", "coucheGS"],
                        arcpy.env.workspace + os.sep + Nom_sortie + "_Buffer")

    # Tri dans les champs retournés
    fields = [field.name for field in arcpy.ListFields(arcpy.env.workspace + os.sep + Nom_sortie) if
            field.name not in ["Num_S", "Nature", fieldDate, datedate_field, "count_overlaps", "OBJECTID", "Shape", "Shape_Length", "Shape_Area","OBJECTID_1", "OBJECTID_12"]]
    for f in fields:
        arcpy.DeleteField_management(arcpy.env.workspace + os.sep + Nom_sortie, f)
    arcpy.RepairGeometry_management(arcpy.env.workspace + os.sep + Nom_sortie)
    arcpy.Delete_management("coucheSentinel")
    arcpy.Delete_management("coucheSentinel_Buffer")
    arcpy.Delete_management("coucheVIIRS")
    arcpy.Delete_management("coucheDSCGR")
    arcpy.Delete_management("coucheGS")