import arcpy
from methodes import *

def creation_table_relation(gdb, seuil, buffer, datedate_field, CoucheTOT, CoucheTOT_Buffer, TableRel, SortedCoucheTOT, ChampCoucheTOT, ChampTableRel):
    arcpy.Delete_management(CoucheTOT_Buffer)
    arcpy.Buffer_analysis(CoucheTOT, CoucheTOT_Buffer, buffer)

    #########TRAITEMENT DES DONNEES#########
    arcpy.AddMessage("Traitement pour creer une table de relation complete SANS SEUIL")
    arcpy.AddMessage("Recuperation des information sur la couche Totale: " + SortedCoucheTOT + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    arcpy.Delete_management(gdb + "/" + SortedCoucheTOT)
    arcpy.Sort_management(CoucheTOT_Buffer, gdb + "/" + SortedCoucheTOT, [datedate_field, "Num_S"])
    arcpy.MakeFeatureLayer_management(gdb + "/" + SortedCoucheTOT, SortedCoucheTOT)
    SGeom = [list(s) for s in arcpy.da.SearchCursor(SortedCoucheTOT, ChampCoucheTOT)]
    NGeom = len(SGeom)

    arcpy.AddMessage(str(NGeom) + " entites recuperees sur la couche Totale triée" + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    arcpy.AddMessage("Creation de la table d'intersection " + TableRel + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    if arcpy.Exists(gdb + "/" + TableRel):
        arcpy.Delete_management(gdb + "/" + TableRel)

    arcpy.CreateTable_management(gdb, TableRel)
    arcpy.MakeTableView_management(gdb + "/" + TableRel, TableRel)

    arcpy.AddField_management(TableRel, "Num_S", "TEXT",field_length=255)
    arcpy.AddField_management(TableRel, datedate_field, "DATE")
    arcpy.AddField_management(TableRel, datedate_field + "_1", "DATE")
    arcpy.AddField_management(TableRel, "Nature", "TEXT", field_length=10)
    arcpy.AddField_management(TableRel, "Num_S_1", "TEXT", field_length=255)
    arcpy.AddField_management(TableRel, "Nature_1", "TEXT", field_length=10)
    arcpy.AddField_management(TableRel, "RelationNature", "TEXT", field_length=10)
    arcpy.AddField_management(TableRel, "Delta", "LONG")
    arcpy.AddMessage("Generation de l'intersection de la couche " + SortedCoucheTOT + " sur elle meme avec critere 'Overlaps'")
    SGeom2 = [sg1 for sg1 in SGeom]
    SGeom2.pop(0)
    SGeom.pop()

    arcpy.AddMessage("Taille des données à traiter : {} entitées".format(len(SGeom)))
    for sgi, sg in enumerate(SGeom):
        date_sg = sg[2]
        if sgi%100 == 0:
            PourcentageTraitementBis(sgi, NGeom)
        for sg2 in SGeom2:
            date_sg2 = sg2[2]
            if (date_sg2 - date_sg).days > seuil:
                break
            if sg[3].overlaps(sg2[3]):
                if sg[1] == 'S' and sg2[1] == 'S':
                    Delta = abs((date_sg-date_sg2).days)
                    if date_sg < date_sg2:
                        iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
                        iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + "2 - " + sg2[1] + "1", Delta])
                        del iCurs
                    else:
                        iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
                        iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + "1 - " + sg2[1] + "2", Delta])
                        del iCurs

                elif sg[1] == 'S':
                    Delta = (date_sg - date_sg2).days
                    if Delta >= 0:
                        iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
                        iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + " - " + sg2[1], Delta])
                        del iCurs

                elif sg2[1] == 'S':
                    Delta = (date_sg2 - date_sg).days
                    if Delta >= 0:
                        iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
                        iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + " - " + sg2[1], Delta])
                        del iCurs
        SGeom2.pop(0)

def verification_table_rel(TableRel):
    if "Doublon" in [f.name for f in  arcpy.ListFields(TableRel)]:
        arcpy.DeleteField_management(TableRel, "Doublon")
    arcpy.AddField_management(TableRel, "Doublon", "TEXT", field_length=255)
    uCurs = arcpy.da.UpdateCursor(TableRel, ["Num_S", "Num_S_1", "RelationNature", "Doublon"])
    for u in uCurs:
        if u[2] == "V - S" or u[2] == "S - V":
            nb1 = int(u[0][1:])
            nb2 = int(u[1][1:])
            if nb1 > nb2:
                u[3] = "VS-" + str(nb2) + "-" + str(nb1)
                uCurs.updateRow(u)
            else:
                u[3] = "VS-" + str(nb1) + "-" + str(nb2)
                uCurs.updateRow(u)
        elif u[2] == "D - S" or u[2] == "S - D":
            nb1 = int(u[0][1:])
            nb2 = int(u[1][1:])
            if nb1 > nb2:
                u[3] = "DS-" + str(nb2) + "-" + str(nb1)
                uCurs.updateRow(u)
            else:
                u[3] = "DS-" + str(nb1) + "-" + str(nb2)
                uCurs.updateRow(u)
        elif u[2] == "GS - S":
            nb1 = int(u[0][2:])
            nb2 = int(u[1][1:])
            if nb1 > nb2:
                u[3] = "GSS-" + str(nb2) + "-" + str(nb1)
                uCurs.updateRow(u)
            else:
                u[3] = "GSS-" + str(nb1) + "-" + str(nb2)
                uCurs.updateRow(u)
        elif u[2] == "S - GS":
            nb1 = int(u[0][1:])
            nb2 = int(u[1][2:])
            if nb1 > nb2:
                u[3] = "GSS-" + str(nb2) + "-" + str(nb1)
                uCurs.updateRow(u)
            else:
                u[3] = "GSS-" + str(nb1) + "-" + str(nb2)
                uCurs.updateRow(u)
        else:
            u[3] = "SS" + str(int(u[0][1:]) + int(u[1][1:]))
            nb1 = int(u[0][1:])
            nb2 = int(u[1][1:])
            if nb1 > nb2:
                u[3] = "SS-" + str(nb2) + "-" + str(nb1)
                uCurs.updateRow(u)
            else:
                u[3] = "SS-" + str(nb1) + "-" + str(nb2)
                uCurs.updateRow(u)
    del uCurs
    arcpy.DeleteIdentical_management(TableRel, ["Doublon"])
    arcpy.Delete_management(TableRel)

def creation_dico(gdb, TableRel, ChampTableRel):
    arcpy.MakeTableView_management(gdb + "/" + TableRel, TableRel)
    Relations = [list(r) for r in arcpy.da.SearchCursor(TableRel, ChampTableRel)]
    arcpy.AddMessage(str(len(Relations)) + " Relations sans doublon")
    arcpy.Delete_management(TableRel)
    arcpy.AddMessage("Recuperation des divers types de References: VIIRS, Groupe Sentinel An-1, DSCGR: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    S_ID1 = list(set([v[0] for v in Relations if v[1] == "S"])) # v[1] est le champ Nature
    S_ID2 = list(set([v[3] for v in Relations if v[4] == "S"])) # rspct Nature_1
    Sent = list()
    Sent.extend(S_ID1)
    del S_ID1
    Sent.extend(S_ID2)
    del S_ID2
    Sent = list(set(Sent))

    # VIIRS
    ViirsID1 = list(set([v[0] for v in Relations if v[1] == "V"]))
    ViirsID2 = list(set([v[3] for v in Relations if v[4] == "V"]))
    Viirs = list()
    Viirs.extend(ViirsID1)
    del ViirsID1
    Viirs.extend(ViirsID2)
    del ViirsID2
    Viirs = list(set(Viirs))
    Viirs.sort()

    # DSCGR
    DID1 = list(set([v[0] for v in Relations if v[1] == "D"]))
    DID2 = list(set([v[3] for v in Relations if v[4] == "D"]))
    D = list()
    D.extend(DID1)
    del DID1
    D.extend(DID2)
    del DID2
    D = list(set(D))

    # Ancien incendies Sentinel Regroupes precedemment
    GSID1 = list(set([v[0] for v in Relations if v[1] == "G"]))
    GSID2 = list(set([v[3] for v in Relations if v[4] == "G"]))
    GS = list()
    GS.extend(GSID1)
    del GSID1
    GS.extend(GSID2)
    del GSID2
    GS = list(set(GS))
    return Relations,Sent,Viirs,D,GS
