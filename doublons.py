import os

import arcpy


def ChampsFcIn(fcIn):
        fields = arcpy.ListFields(fcIn)
        fieldName = []
        for field in fields:
                fieldName.append(field.name)
        return fieldName

def GenererIdDoublons(fcIn, chemin, listFields, typeDoublon, nomFile):
        outTable = chemin + "TableDoublonP" + typeDoublon + "_" + fcIn.split(os.path.sep)[-1].split("_")[-1]
        try :
                arcpy.Delete_management(outTable)
        except:
                pass
        arcpy.AddMessage("fcIn => {0}\noutTable => {1}\nlistFields => {2}".format(fcIn, outTable, listFields))
        arcpy.FindIdentical_management(in_dataset=fcIn, out_dataset=outTable, fields=listFields, output_record_option="ONLY_DUPLICATES")
        # arcpy.FindIdentical()
        fieldName = ChampsFcIn(fcIn)
        if "ID_P"+typeDoublon in fieldName:
                arcpy.AddMessage( "\n Doublons P" + typeDoublon +" deja calcules, nouveau calcul ")
                arcpy.DeleteField_management(fcIn, "ID_P"+typeDoublon)
            
        if arcpy.management.GetCount(outTable)[0] != "0":         
                arcpy.JoinField_management(fcIn, "OBJECTID", outTable, "IN_FID", "FEAT_SEQ")
                arcpy.AlterField_management(fcIn,"FEAT_SEQ",new_field_name="ID_P"+ typeDoublon) #change le nom du champs
                nb = int(arcpy.GetCount_management(outTable).getOutput(0))
                nomFile.write("\n Nombre de doublons P" + typeDoublon + " => {0} ".format(nb))
                max_value = arcpy.da.SearchCursor(outTable, "FEAT_SEQ", "FEAT_SEQ IS NOT NULL", sql_clause = (None, "ORDER BY FEAT_SEQ DESC")).next()[0]
                nomFile.write("\n Nombre de groupe de doublons P" + typeDoublon + " => {0} ".format(max_value))
                arcpy.AddMessage("\n Nombre de groupe de doublons P" + typeDoublon + " => {0} ".format(max_value))
        else:
                arcpy.AddMessage("\n Il n'y a pas de doublons P" + typeDoublon)
                nomFile.write("\n Il n'y a pas de doublons P" + typeDoublon)

def supression_doublons(fcIn, gdb):
    try:
        fcInName = fcIn.split(os.path.sep)[-1]
    except:
        fcInName = fcIn
    for field in arcpy.ListFields(fcIn):
            if field.type == "Date":
                    dateFieldName = field.name
    if gdb[-4:] != ".gdb":
            gdb += ".gdb"
    chemin = gdb + os.path.sep
    DoublonsResult = chemin + "DoublonsDefinis_" + fcInName 
    SansDoublon = chemin + "SansDoublonsResult_" + fcInName

    try:
            arcpy.CopyFeatures_management(fcIn, DoublonsResult)
            arcpy.AddMessage("CopyFeatures done")
    except:
            arcpy.AddMessage("retry to copy features...")
            arcpy.Delete_management(DoublonsResult)
            arcpy.CopyFeatures_management(fcIn, DoublonsResult)
            arcpy.AddMessage("CopyFeatures done")
    # Stockage des informations doublons dans un fichier .txt
    with open(chemin + "ctrl_doublons.txt", "w") as f:
            f.write("##################### Controle des doublons #####################\n")
            GenererIdDoublons(DoublonsResult, chemin, ["Shape", dateFieldName, "nom"], "1", f)
            GenererIdDoublons(DoublonsResult, chemin, ["Shape", dateFieldName], "2", f)
            GenererIdDoublons(DoublonsResult, chemin, ["Shape"], "3", f)

            arcpy.Delete_management(SansDoublon)    
            arcpy.CopyFeatures_management(DoublonsResult, SansDoublon)
            arcpy.DeleteIdentical_management(SansDoublon, ["Shape", dateFieldName])
            f.write("\nNombre de polygones apres elimination des doublons => {0}".format(arcpy.GetCount_management(SansDoublon).getOutput(0)))
            f.close()

