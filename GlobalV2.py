# -*- coding: utf8 -*-

# ----------------------------------------------------------------------------------------------
# Script           : Global.py
# Author           : Côme DAVAL
# Date             : 07/04/2021
# Object           : Chaine de traitement complète
# ----------------------------------------------------------------------------------------------
import sys, os
# import arcgisscripting
import arcpy
from FctArcpy import *
from methodes import *
from os import chdir
import datetime as dt

sys.setrecursionlimit(10000)
arcpy.AddMessage("Limite de la récursion : " + str(sys.getrecursionlimit()))
arcpy.env.parallelProcessingFactor = "90%"



# ------------------------------VARIABLES----------------------------------------
gdb = arcpy.GetParameterAsText(0) # Nom de la gdb
bruts = arcpy.GetParameter(1) # Liste des shp à combiner
annee_etude = int(arcpy.GetParameterAsText(2)) # Annee de l'étude
champDate = arcpy.GetParameterAsText(3) # Nom du champ date
Couche_MOS = arcpy.GetParameterAsText(4) # Nom de la couche MOS brutes
Couche_DSCGR = arcpy.GetParameterAsText(5) # Nom de la couche DSCGR
date_dscgr = arcpy.GetParameterAsText(6)
Couche_VIIRS = arcpy.GetParameterAsText(7) # Nom de la couche VIIRS
date_viirs = arcpy.GetParameterAsText(8)
Couche_GROUPE = arcpy.GetParameterAsText(9) # Nom de la couche Sentinel An-1
date_groupe = arcpy.GetParameterAsText(10)
seuil = int(arcpy.GetParameterAsText(11)) # Seuillage des incendies (défaut : 30j)
buffer = arcpy.GetParameterAsText(12) + " meters" # Buffer (défaut : 100m)

# gdb = r"C:\Users\come.daval\Documents\Sentinel_Global\Sentinel.gdb" # Nom de la gdb
# bruts = [r"C:\Users\come.daval\Documents\Sentinel_Global\Données initiales\ShapeFiles\S2_L2A_BurnedAreas_0" + str(r) for r in range(1, 10)]
# bruts += [r"C:\Users\come.daval\Documents\Sentinel_Global\Données initiales\ShapeFiles\S2_L2A_BurnedAreas_" + str(r) for r in range(10, 13)]
# bruts += [r"C:\Users\come.daval\Documents\Sentinel_Global\Données initiales\ShapeFiles\S2_L2A_BurnedAreas_" + str(r) for r in range(2101, 2103)] # Liste des shps à combiner
# for i in range(len(bruts)):
#     bruts[i] += ".shp"
# annee_etude = 2020 # Annee de l'étude
# champDate = "date" # Nom du champ date
# Couche_MOS = r"C:\Users\come.daval\Documents\Sentinel_Global\Sentinel.gdb\MOS" # Nom de la couche MOS brutes
# Couche_DSCGR = r"C:\Users\come.daval\Documents\Sentinel_Global\Sentinel.gdb\DSCGR" # Nom de la couche DSCGR
# date_dscgr = "date_date"
# Couche_VIIRS = r"C:\Users\come.daval\Documents\Sentinel_Global\Sentinel.gdb\VIIRS" # Nom de la couche VIIRS
# date_viirs = "Fin"
# Couche_GROUPE = r"C:\Users\come.daval\Documents\Sentinel_Global\Sentinel.gdb\SENTINEL_2019" # Nom de la couche Sentinel An-1
# date_groupe = "MAX_BegDate"
# seuil = 40 # Seuillage des incendies (défaut : 30j)
# buffer = "100 meters" # Buffer (défaut : 100m)

arcpy.env.workspace = gdb
Merged_Data = "Merged_Data"
Couche_MOS_Select = Couche_MOS + "_Select"
checkGeomResult = arcpy.env.workspace + os.path.sep + "checkGeomResult"
Merged_Data_SS_Doublons = "SansDoublonsResult_Merged_Data"
Merged_Data_SS_Ab = "SansDoublonsResult_Merged_Data_SansAb"
Merged_Data_Inter_MOS = Merged_Data + "_Inter_MOS"
Fusion_Data = "Fusion_Data"
ListCoucheRef = [Couche_DSCGR, Couche_VIIRS, Couche_GROUPE]
ListChampsDate = [date_dscgr, date_viirs, date_groupe]
champ_cat_mos = "l_2014_n3"
datedate_field = "date_date"
where_clause_mos = "l_2014_n3 = 'Tissu urbain discontinu'"
where_clause_mos += " Or l_2014_n3 = 'Réseaux de communication'"
where_clause_mos += " Or l_2014_n3 = 'Tissu urbain continu' "
where_clause_mos += " Or l_2014_n3 = 'Mines, décharges minières, infrastructures et chantiers miniers'"
where_clause_mos += " Or l_2014_n3 = 'Zones industrielles ou commerciales et équipements'"
where_clause_mos += " Or l_2014_n3 = 'Zones humides intérieures'"
where_clause_mos += " Or l_2014_n3 = 'Plages, dunes et sable'"
where_clause_mos += " Or l_2014_n3 = 'Plages, dunes, sable'"
where_clause_mos += " Or l_2014_n3 = 'Roches et sols nus'"
where_clause_mos += " Or l_2014_n3 = 'Eaux maritimes'"
ObjectID_Org_Layer = "OBJECTID_1" # ID de la couche d'origine du feu dans la table intersection
MinPCT = 0.00  # Minimum de pourcentage de surface en commun avec un
                #polygone feu que doit posseder une classe. Vaut 0.00 par defaut
MinPCTAb = 25 # Pourcentage au dessus du quel le feu est considéré comme aberrant

for champ, couche in zip(ListChampsDate, ListCoucheRef):
    if champ != datedate_field:
        arcpy.AddField_management(couche, datedate_field, "Date")
        arcpy.CalculateField_management(couche, datedate_field, "!" + champ + "!")


# # # ------------------------------DELETE----------------------------------------
# arcpy.Delete_management("Merged_Data")
# arcpy.Delete_management(checkGeomResult)

# # --------------------Fusion et ajout d'un champ Date-------------------------
# arcpy.AddMessage("Fusion et ajout d'un champ Date")
# arcpy.Merge_management(bruts, Merged_Data)
# date_field = arcpy.ListFields(Merged_Data, champDate).pop()
# if date_field.type != "Date":
#     arcpy.AddField_management(Merged_Data, "date_date", "Date")
#     # arcpy.CalculateField_management(Merged_Data, "date_date", "datetime.strptime(!"+champDate+"!, '%Y%m%d')")
#     arcpy.CalculateField_management(Merged_Data, "date_date", "datetime.datetime.strptime(!"+champDate+"!, '%Y%m%d')")

#     # arcpy.CalculateField_management(Merged_Data, "date_date", "datetime.datetime.strptime(!"+champDate+"!, '%Y-%m-%d')")

# arcpy.AddMessage("Done !")

# # ------------------------------Réparation des géométries----------------------------------------
# fcIn = Merged_Data
# arcpy.RepairGeometry_management(fcIn, True)

# # ------------------------------Vérification des géométries--------------------------------------
# fcIn = Merged_Data
# arcpy.CheckGeometry_management(fcIn, checkGeomResult)
# nbPbGeom = int(arcpy.GetCount_management(checkGeomResult)[0])
# arcpy.AddMessage("{} problème de géométrie restant à traiter".format(nbPbGeom))
# if int(nbPbGeom) > 0:
#     arcpy.AddMessage("Erreur de géométrie")
#     sys.exit()

# # ------------------------------Doublons----------------------------------------
# fcIn = Merged_Data
# try:
#     fcInName = fcIn.split(os.path.sep)[-1]
# except:
#     fcInName = fcIn
# for field in arcpy.ListFields(fcIn):
#         if field.type == "Date":
#                 dateFieldName = field.name
# if gdb[-4:] != ".gdb":
#         gdb += ".gdb"
# chemin = gdb + os.path.sep
# DoublonsResult = chemin + "DoublonsDefinis_" + fcInName 
# SansDoublon = chemin + "SansDoublonsResult_" + fcInName

# try:
#         arcpy.CopyFeatures_management(fcIn, DoublonsResult)
#         arcpy.AddMessage("CopyFeatures done")
# except:
#         arcpy.AddMessage("retry to copy features...")
#         arcpy.Delete_management(DoublonsResult)
#         arcpy.CopyFeatures_management(fcIn, DoublonsResult)
#         arcpy.AddMessage("CopyFeatures done")
# # Stockage des informations doublons dans un fichier .txt
# with open(chemin + "ctrl_doublons.txt", "w") as f:
#         f.write("##################### Controle des doublons #####################\n")
#         GenererIdDoublons(DoublonsResult, chemin, ["Shape", dateFieldName, "nom"], "1", f)
#         GenererIdDoublons(DoublonsResult, chemin, ["Shape", dateFieldName], "2", f)
#         GenererIdDoublons(DoublonsResult, chemin, ["Shape"], "3", f)

#         arcpy.CopyFeatures_management(DoublonsResult, SansDoublon)
#         arcpy.DeleteIdentical_management(SansDoublon, ["Shape", dateFieldName])
#         f.write("\nNombre de polygones apres elimination des doublons => {0}".format(arcpy.GetCount_management(SansDoublon).getOutput(0)))
#         f.close()

# # ------------------------------Aberrations MOS----------------------------------------
# # Extraction des catégories MOS utilisées
# arcpy.Delete_management(Couche_MOS_Select)
# arcpy.Delete_management(Merged_Data_Inter_MOS)
# arcpy.Delete_management(Merged_Data_SS_Ab)
# arcpy.Select_analysis(Couche_MOS, Couche_MOS_Select, where_clause_mos)
# arcpy.TabulateIntersection_analysis(Merged_Data_SS_Doublons, "OBJECTID", Couche_MOS_Select, Merged_Data_Inter_MOS, champ_cat_mos, out_units= "HECTARES",)

# # Recuperation des entrees
# Layer1 = Merged_Data_SS_Doublons
# Tb_Intersect = Merged_Data_Inter_MOS
# FieldOIDLayer1 = ObjectID_Org_Layer  
# FieldClasse = champ_cat_mos
# FieldPercentage = "PERCENTAGE"
# SortieChampClasse = "CLASSE"
# SortieChampPCT = "PERCENTAGE"

# fieldsAberrant = ['Eaux maritimes',
#             'Mines, décharges minières, infrastructures et chantiers miniers',
#             'Plages, dunes et sable', 'Plages, dunes, sable', 'Roches et sols nus',
#             'Réseaux de communication', 'Tissu urbain continu', 'Tissu urbain discontinu',
#             'Zones humides intérieures', 'Zones industrielles ou commerciales et équipements']

# SortieChampClasseAb = "CLASSE_Ab"
# SortieChampPCTAb = "PERCENTAGE_Ab"
# SortieChampSommeAb = "SUM_PERCENTAGE_Ab"

# # arcpy.AddMessage("recuperation des champs ID de la couche et de la table")
# FieldOIDTb = recup_oid(Tb_Intersect)
# FieldOIDC1 = recup_oid(Layer1)

# # Dictionnaire pour lequel les cles correspondent aux IDs de la couche en entrée
# # au quelles sont associees des listes contenant la liste des noms de Classe,
# # la liste des pourcentages associees, la liste des classes aberrantes,
# # la liste des pourcentages associees, la somme des pourcentages des
# # champs aberrants, et la mention de supression

# sCurs = arcpy.da.SearchCursor(Tb_Intersect, [FieldOIDLayer1, FieldClasse, FieldPercentage],
#                                 where_clause=FieldPercentage + " >= " + str(MinPCT),
#                                 sql_clause=(None, "ORDER BY " + FieldOIDTb))
# dico = DicoTableInters(sCurs, FieldClasse, Tb_Intersect, fieldsAberrant, MinPCTAb, MinPCT)

# # On s'occupe des champs de sortie de la couche d'entree
# Champs = [SortieChampClasse, SortieChampPCT, SortieChampClasseAb, SortieChampPCTAb, SortieChampSommeAb, 'A_SUPPRIMER']
# CreateChamps(Layer1, dico, Champs)

# uCurs = arcpy.da.UpdateCursor(Layer1,
#                                 [FieldOIDC1, SortieChampClasse, SortieChampPCT, SortieChampClasseAb, SortieChampPCTAb,
#                                 SortieChampSommeAb, 'A_SUPPRIMER'], sql_clause=(None, "ORDER BY " + FieldOIDC1))
# update_layer1(uCurs, dico)

# # Creation d'une couche d'entites sans aberrations
# arcpy.MakeFeatureLayer_management(Layer1, 'Layer1',"A_SUPPRIMER IS NULL OR A_SUPPRIMER LIKE ''")
# arcpy.CopyFeatures_management('Layer1', gdb + os.path.sep + Layer1.split('\\')[-1] + "_SansAb")
# arcpy.Delete_management('Layer1')

# #################### Indice de confiance #####################
# arcpy.AddMessage("Debut du processus Indice de confiance : " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# couche = Merged_Data_SS_Ab
# # couche = "Merged_Data_1"
# seuilSurface = .6

# coucheTravail = "Merged_Data_Trust"
# champs = ["OBJECTID", "Shape@", "liste_overlaps", "count_overlaps", "date_date"]
# arcpy.Delete_management(gdb + "/" + coucheTravail)
# arcpy.Delete_management(coucheTravail)
# arcpy.MakeFeatureLayer_management(gdb + "/" + couche, coucheTravail)
# arcpy.Sort_management(coucheTravail, coucheTravail, [datedate_field])
# arcpy.AddField_management(coucheTravail, "liste_overlaps", "Text")
# arcpy.AddField_management(coucheTravail, "count_overlaps", "Double")
# sCurs1 = [list(i) for i in arcpy.da.SearchCursor(coucheTravail, champs)]
# sCurs2 = [i for i in sCurs1]
# sCurs1.pop()
# sCurs2.pop(0)
# dico = {}
# l = len(sCurs1)
# for index, s1 in enumerate(sCurs1):
#     dico[s1[0]] = []
#     if index%100 == 0:
#         arcpy.AddMessage('{:.1f}% analysé'.format(index/l*100))
#     for s2 in sCurs2:
#         if (s2[4] - s1[4]).days > seuil:
#             break
#         if s1[1].disjoint(s2[1]):
#             continue
#         s_inter = s1[1].intersect(s2[1], 4)
#         area = s_inter.getArea("GEODESIC", "SQUAREMETERS")
#         area_org = s1[1].getArea("GEODESIC", "SQUAREMETERS")
#         rap = area/area_org
#         if rap >= seuilSurface:
#             dico[s1[0]].append([s2[0], area, rap])  
#     sCurs2.pop(0)
#     # arcpy.AddMessage(dico)

# uCurs = arcpy.da.UpdateCursor(coucheTravail, champs)
# for u in uCurs:
#     if u[0] in dico.keys() and dico[u[0]] != []:
#         u[2] = ''
#         u[3] = 0
#         for ol in dico[u[0]]:
#             try:
#                 u[2] += str(ol[0]) + ', '
#                 u[3] += 1
#             except TypeError:
#                 u[3] += 1
#                 pass
#         try:
#             uCurs.updateRow(u)
#         except RuntimeError:
#             arcpy.AddMessage("Valeur invalide")
#             u[2] = "Invalide"
#             uCurs.updateRow(u)
# try:
#     arcpy.CopyFeatures_management(coucheTravail, gdb + "/" + coucheTravail)
# except :
#     arcpy.Delete_management(gdb + "/" + coucheTravail)
#     arcpy.CopyFeatures_management(coucheTravail, gdb + "/" + coucheTravail)

# # ------------------------------Références----------------------------------------
# arcpy.AddMessage("Debut du processus d'ajout des références : " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
# # Ajout des références
# l_couches = [Merged_Data_SS_Ab, Couche_DSCGR, Couche_VIIRS, Couche_GROUPE]
# # l_couches = [coucheTravail, Couche_DSCGR, Couche_VIIRS, Couche_GROUPE]
# list_nature = ["S", "D", "V", "G"]
# list_oid = ["OBJECTID"]*4

# # creation des champs  Nature et Num_S pour ne pas perdre l'origine de la couche et les identifiants avant fusion
# for i in range(len(list_nature)):
#     arcpy.MakeFeatureLayer_management(l_couches[i], "couche" + list_nature[i])
#     add_field_Nature_Num("couche" + list_nature[i], list_nature[i], list_oid[i])
#     arcpy.Delete_management("couche" + list_nature[i])

# # MeF des champs date
# for couche, dateName in zip(ListCoucheRef, ListChampsDate):
#     date_field = arcpy.ListFields(couche, "date")
#     # if couche == Couche_GROUPE:
#     #     continue
#     if len(date_field)>0:
#         date_f = date_field.pop()
#         if date_f.type == "String":
#             continue
#         else:
#             # arcpy.DeleteField_management(couche, date_f)
#             pass
#     # Nom du champ date, au format str, en sortie, défaut : date
#     dateNewName = "date"
#     arcpy.AddField_management(couche, dateNewName, 'String')
#     try:
#         arcpy.CalculateField_management(couche, dateNewName, "datetime.datetime.strftime(!"+dateName+"!, '%Y%m%d')")
#     except TypeError:
#         arcpy.CalculateField_management(couche, dateNewName, "!" + dateName + "!")

# fcSentinel = Merged_Data_SS_Ab
# # fcSentinel = coucheTravail
# fcDSCGR = Couche_DSCGR
# fcVIIRS = Couche_VIIRS
# fcGS = Couche_GROUPE
# fieldDate = "date"
# Nom_sortie = Fusion_Data  # nom de la couche en sortie
# # WoorkIngdb()
# dateDebut = str(annee_etude) + '0101'
# dateFin = str(annee_etude+1) + '0301'
# dateDebutRef = str(annee_etude-1) + '0101'
# where_clause = fieldDate + " >= '" + dateDebut + "' AND " + fieldDate + " < '" + dateFin + "'"
# where_clause_ref = fieldDate + " >= '" + dateDebutRef + "' AND " + fieldDate + " < '" + dateFin + "'"
# arcpy.AddMessage(dateDebut)
# arcpy.AddMessage(dateFin)
# arcpy.AddMessage(dateDebutRef)

# arcpy.Delete_management(Fusion_Data)

# # Selection des polygones de l'annee d'etude (01/01/annee_etude - 31/02/annee_etude+1)
# arcpy.MakeFeatureLayer_management(fcSentinel, "coucheSentinel", where_clause=where_clause)
# # Selection des polygones de reference (01/01/annee_etude-1 - 31/02/annee_etude+1)
# arcpy.MakeFeatureLayer_management(fcDSCGR, "coucheDSCGR", where_clause=where_clause_ref)
# arcpy.MakeFeatureLayer_management(fcVIIRS, "coucheVIIRS", where_clause=where_clause_ref)
# arcpy.MakeFeatureLayer_management(fcGS, "coucheGS", where_clause=where_clause_ref)

# # Fusion des tables
# arcpy.Merge_management(["coucheSentinel", "coucheDSCGR", "coucheVIIRS", "coucheGS"],
#                         arcpy.env.workspace + os.sep + Nom_sortie)
# # Tri dans les champs retournés
# fields = [field.name for field in arcpy.ListFields(arcpy.env.workspace + os.sep + Nom_sortie) if
#             field.name not in ["Num_S", "Nature", fieldDate, datedate_field, "count_overlaps", "OBJECTID", "Shape", "Shape_Length", "Shape_Area","OBJECTID_1", "OBJECTID_12"]]
# for f in fields:
#     arcpy.DeleteField_management(arcpy.env.workspace + os.sep + Nom_sortie, f)
# arcpy.RepairGeometry_management(arcpy.env.workspace + os.sep + Nom_sortie)
# arcpy.Delete_management("coucheSentinel")
# arcpy.Delete_management("coucheVIIRS")
# arcpy.Delete_management("coucheDSCGR")
# arcpy.Delete_management("coucheGS")

# # ------------------------------REGROUPEMENT----------------------------------------


# arcpy.AddMessage("Debut du processus Regroupement : " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
# CoucheTOT = Fusion_Data
# # ChampCoucheTOT = ["Num_S", "Nature", datedate_field, "Shape@", "OBJECTID", "count_overlaps"]
# ChampCoucheTOT = ["Num_S", "Nature", datedate_field, "Shape@", "OBJECTID"]

# ChampTableRel = ["Num_S", "Nature", datedate_field, "Num_S_1", "Nature_1", datedate_field + "_1", "RelationNature", "Delta"]
# ChampIDSentinel = "Num_S"
# CoucheTOT_Buffer = CoucheTOT + "_Buffer"
# TableRel = CoucheTOT + "_OverlapsALL" + str(seuil) + "j"
# SortedCoucheTOT = CoucheTOT + "_Sorted"
# arcpy.AddMessage(TableRel)
# ######### Zone tampon de 100m sur les données fusionnées #######
# arcpy.Delete_management(CoucheTOT_Buffer)
# arcpy.Buffer_analysis(CoucheTOT, CoucheTOT_Buffer, buffer)

# #########TRAITEMENT DES DONNEES#########
# arcpy.AddMessage("Traitement pour creer une table de relation complete SANS SEUIL")
# arcpy.AddMessage("Recuperation des information sur la couche Totale: " + SortedCoucheTOT + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
# arcpy.Delete_management(gdb + "/" + SortedCoucheTOT)
# arcpy.Sort_management(CoucheTOT_Buffer, gdb + "/" + SortedCoucheTOT, [datedate_field, "Num_S"])
# arcpy.MakeFeatureLayer_management(gdb + "/" + SortedCoucheTOT, SortedCoucheTOT)
# SGeom = [list(s) for s in arcpy.da.SearchCursor(SortedCoucheTOT, ChampCoucheTOT)]
# NGeom = len(SGeom)

# arcpy.AddMessage(str(NGeom) + " entites recuperees sur la couche Totale triée" + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
# arcpy.AddMessage("Creation de la table d'intersection " + TableRel + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# if arcpy.Exists(gdb + "/" + TableRel):
#     arcpy.Delete_management(gdb + "/" + TableRel)

# arcpy.CreateTable_management(gdb, TableRel)
# arcpy.MakeTableView_management(gdb + "/" + TableRel, TableRel)

# arcpy.AddField_management(TableRel, "Num_S", "TEXT",field_length=255)
# arcpy.AddField_management(TableRel, datedate_field, "DATE")
# arcpy.AddField_management(TableRel, datedate_field + "_1", "DATE")
# arcpy.AddField_management(TableRel, "Nature", "TEXT", field_length=10)
# arcpy.AddField_management(TableRel, "Num_S_1", "TEXT", field_length=255)
# arcpy.AddField_management(TableRel, "Nature_1", "TEXT", field_length=10)
# arcpy.AddField_management(TableRel, "RelationNature", "TEXT", field_length=10)
# arcpy.AddField_management(TableRel, "Delta", "LONG")
# arcpy.AddMessage("Generation de l'intersection de la couche " + SortedCoucheTOT + " sur elle meme avec critere 'Overlaps'")
# SGeom2 = [sg1 for sg1 in SGeom]
# SGeom2.pop(0)
# SGeom.pop()
# table = []
# arcpy.AddMessage("Taille des données à traiter : {} entitées".format(len(SGeom)))
# for sgi, sg in enumerate(SGeom):
#     date_sg = sg[2]
#     if sgi%100 == 0:
#         PourcentageTraitementBis(sgi, NGeom)
#     for sg2 in SGeom2:
#         date_sg2 = sg2[2]
#         if (date_sg2 - date_sg).days > seuil:
#             break
#         if sg[3].overlaps(sg2[3]):
#             if sg[1] == 'S' and sg2[1] == 'S':
#                 Delta = abs((date_sg-date_sg2).days)
#                 if date_sg < date_sg2:
#                     iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
#                     iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + "2 - " + sg2[1] + "1", Delta])
#                     del iCurs
#                 else:
#                     iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
#                     iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + "1 - " + sg2[1] + "2", Delta])
#                     del iCurs

#             elif sg[1] == 'S':
#                 Delta = (date_sg - date_sg2).days
#                 if Delta >= 0:
#                     iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
#                     iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + " - " + sg2[1], Delta])
#                     del iCurs

#             elif sg2[1] == 'S':
#                 Delta = (date_sg2 - date_sg).days
#                 if Delta >= 0:
#                     iCurs = arcpy.da.InsertCursor(TableRel, ChampTableRel)
#                     iCurs.insertRow([sg[0], sg[1], date_sg, sg2[0], sg2[1], date_sg2, sg[1] + " - " + sg2[1], Delta])
#                     del iCurs
#     SGeom2.pop(0)

# arcpy.AddMessage("Recuperation des informations de la Table de proximite " + TableRel + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
# ### Code qui remplace la fonction RelationDouble pour optimisation #####
# if "Doublon" in [f.name for f in  arcpy.ListFields(TableRel)]:
#     arcpy.DeleteField_management(TableRel, "Doublon")
# arcpy.AddField_management(TableRel, "Doublon", "TEXT", field_length=255)
# uCurs = arcpy.da.UpdateCursor(TableRel, ["Num_S", "Num_S_1", "RelationNature", "Doublon"])
# for u in uCurs:
#     if u[2] == "V - S" or u[2] == "S - V":
#         nb1 = int(u[0][1:])
#         nb2 = int(u[1][1:])
#         if nb1 > nb2:
#             u[3] = "VS-" + str(nb2) + "-" + str(nb1)
#             uCurs.updateRow(u)
#         else:
#             u[3] = "VS-" + str(nb1) + "-" + str(nb2)
#             uCurs.updateRow(u)
#     elif u[2] == "D - S" or u[2] == "S - D":
#         nb1 = int(u[0][1:])
#         nb2 = int(u[1][1:])
#         if nb1 > nb2:
#             u[3] = "DS-" + str(nb2) + "-" + str(nb1)
#             uCurs.updateRow(u)
#         else:
#             u[3] = "DS-" + str(nb1) + "-" + str(nb2)
#             uCurs.updateRow(u)
#     elif u[2] == "GS - S":
#         nb1 = int(u[0][2:])
#         nb2 = int(u[1][1:])
#         if nb1 > nb2:
#             u[3] = "GSS-" + str(nb2) + "-" + str(nb1)
#             uCurs.updateRow(u)
#         else:
#             u[3] = "GSS-" + str(nb1) + "-" + str(nb2)
#             uCurs.updateRow(u)
#     elif u[2] == "S - GS":
#         nb1 = int(u[0][1:])
#         nb2 = int(u[1][2:])
#         if nb1 > nb2:
#             u[3] = "GSS-" + str(nb2) + "-" + str(nb1)
#             uCurs.updateRow(u)
#         else:
#             u[3] = "GSS-" + str(nb1) + "-" + str(nb2)
#             uCurs.updateRow(u)
#     else:
#         u[3] = "SS" + str(int(u[0][1:]) + int(u[1][1:]))
#         nb1 = int(u[0][1:])
#         nb2 = int(u[1][1:])
#         if nb1 > nb2:
#             u[3] = "SS-" + str(nb2) + "-" + str(nb1)
#             uCurs.updateRow(u)
#         else:
#             u[3] = "SS-" + str(nb1) + "-" + str(nb2)
#             uCurs.updateRow(u)
# del uCurs
# arcpy.DeleteIdentical_management(TableRel, ["Doublon"])
# arcpy.Delete_management(TableRel)
# # ### Fin du Code qui remplace la fonction RelationDouble pour optimisation #####
# arcpy.AddMessage("Fin du processus: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# ------------------------------Etape 2----------------------------------------
arcpy.AddMessage("Debut du processus Etape 2: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
Couche = Fusion_Data
ChampTableRel = ["Num_S", "Nature", "date_date", "Num_S_1", "Nature_1", "date_date_1", "RelationNature", "Delta"]
seuils= [seuil]
ChampIDSentinel = "Num_S"
ChampIDFusions = ["ID_Fusion_" + str(seuil) + "j" for seuil in seuils]
TableRels = [Fusion_Data + "_OverlapsALL" + str(seuil) + "j" for seuil in seuils]

#########TRAITEMENT DES DONNEES####################################
for seuil in seuils:
    ChampIDFusion = ChampIDFusions[seuils.index(seuil)]
    TableRel = TableRels[seuils.index(seuil)]
    arcpy.AddMessage("Traitement pour le seuil " + str(seuil) + " jours")
    arcpy.AddMessage("Recuperation des informations de la Table de proximite " + TableRel + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
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

    #VIIRS
    ViirsID1 = list(set([v[0] for v in Relations if v[1] == "V"]))
    ViirsID2 = list(set([v[3] for v in Relations if v[4] == "V"]))
    Viirs = list()
    Viirs.extend(ViirsID1)
    del ViirsID1
    Viirs.extend(ViirsID2)
    del ViirsID2
    Viirs = list(set(Viirs))
    Viirs.sort()

    #DSCGR
    DID1 = list(set([v[0] for v in Relations if v[1] == "D"]))
    DID2 = list(set([v[3] for v in Relations if v[4] == "D"]))
    D = list()
    D.extend(DID1)
    del DID1
    D.extend(DID2)
    del DID2
    D = list(set(D))

    #Ancien incendies Sentinel Regroupes precedemment
    GSID1 = list(set([v[0] for v in Relations if v[1] == "G"]))
    GSID2 = list(set([v[3] for v in Relations if v[4] == "G"]))
    GS = list()
    GS.extend(GSID1)
    del GSID1
    GS.extend(GSID2)
    del GSID2
    GS = list(set(GS))

    '''CHANGEMENT ORDRE REFERENCE DSCGR puis VIIRS puis Groupe Incendie An-1'''
    arcpy.AddMessage("Classification selon DSCGR: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    RefD = RefSentinel(D, Sent, Relations, "D", seuil)
    dicoD = RefD[0]
    Sent = RefD[1]
    arcpy.AddMessage("Classification secondaire selon DSCGR: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    # dicoSD = InversionDicoRef(dicoD)
    arcpy.AddMessage("Dico ok")

    # return dicoRef, dicoSRef, SNT
    Sent = OrdonnerSentinel(Sent, Relations)
    SentSecD = SentinelSecondaire(dicoD, Relations, seuil, Sent)

    dicoD = SentSecD[0]
    dicoSD = InversionDicoRef(dicoD)
    # dicoSD = SentSecD[1]
    Sent = SentSecD[1]
    Sent = [s for s in Sent if s not in dicoSD.keys()]  # A vérifier utilitée : comparaison Sent et Sent
    arcpy.AddMessage("Longueur du dico inverse {}".format(dicoSD))
    arcpy.AddMessage(str(len(Sent)) + " Sentinels a classer")
    SentiDtest = [s for s in Sent if s[0] == "D"]
    arcpy.AddMessage(SentiDtest)

    if len(Sent) > 0:
        arcpy.AddMessage("Classification selon VIIRS: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        RefVIIRS = RefSentinel(Viirs, Sent, Relations, "V", seuil)
        dicoVIIRS = RefVIIRS[0]
        Sent = RefVIIRS[1]
        arcpy.AddMessage("Classification secondaire selon VIIRS: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        dicoSVIIRS = InversionDicoRef(dicoVIIRS)
        arcpy.AddMessage(dicoSVIIRS)

        # return dicoRef, dicoSRef, SNT
        Sent = OrdonnerSentinel(Sent, Relations)
        SentSecV = SentinelSecondaire(dicoVIIRS, Relations, seuil, Sent)
        dicoVIIRS = SentSecV[0]
        dicoSVIIRS = InversionDicoRef(dicoVIIRS)
        # dicoSVIIRS = SentSecV[1]
        Sent = SentSecV[1]
        Sent = [s for s in Sent if s not in dicoSVIIRS.keys()]
        arcpy.AddMessage(str(len(Sent)) + " Sentinels a classer")

        if len(Sent) > 0:
            arcpy.AddMessage("Classification selon Groupe Incendie An-1: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            RefGS = RefSentinel(GS, Sent, Relations, "G", seuil)
            dicoGS = RefGS[0]
            Sent = RefGS[1]
            arcpy.AddMessage("Classification secondaire selon Groupe Incendie An-1: " + dt.datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"))
            dicoSGS = InversionDicoRef(dicoGS)

            # return dicoRef, dicoSRef, SNT
            Sent = OrdonnerSentinel(Sent, Relations)
            SentSecGS = SentinelSecondaire(dicoGS, Relations, seuil, Sent)
            dicoGS = SentSecGS[0]
            dicoSGS = InversionDicoRef(dicoGS)
            # dicoSGS = SentSecGS[1]
            Sent = SentSecGS[1]
            Sent = [s for s in Sent if s not in dicoSGS.keys()]
            arcpy.AddMessage(dicoSGS)
            arcpy.AddMessage(str(len(Sent)) + " Sentinels a classer")

    if len(Sent) > 0:
        '''Classement Sentinels restant dans l'ordre croissant'''
        Sent = OrdonnerSentinel(Sent, Relations)
        dicoSent = ClasseOnlySentinel(Sent,Relations,seuil)
        arcpy.AddMessage(str(len(Sent)) + " Sentinels a classer")
        #arcpy.AddMessage(dicoSent)

    arcpy.AddMessage("Implementation des identifiants: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    if "/" in Couche:
        arcpy.MakeFeatureLayer_management(gdb + "/" + Couche, Couche.split("/")[1])
    else:
        arcpy.MakeFeatureLayer_management(gdb + "/" + Couche, Couche)

    arcpy.AddMessage("Ajout du champ " + ChampIDFusion)
    FieldsCouche = [f.name for f in arcpy.ListFields(Couche)]
    arcpy.AddMessage(FieldsCouche)
    if ChampIDFusion in FieldsCouche:
        arcpy.DeleteField_management(Couche, ChampIDFusion)
    arcpy.AddField_management(Couche, ChampIDFusion, "TEXT",field_length=255)

    if len(dicoVIIRS.keys()) > 0:
        arcpy.AddMessage("Implementation de " + str(len(dicoVIIRS.keys())) + " ID Fusion lies aux VIIRS: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        ImplementationGroupSID(dicoSVIIRS, Couche, ChampIDSentinel, ChampIDFusion)

    if len(dicoGS.keys()) > 0:
        arcpy.AddMessage("Implementation des " + str(len(dicoGS.keys())) + " ID Fusion lies aux Groupe Sentinel An-1: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        ImplementationGroupSID(dicoSGS, Couche, ChampIDSentinel, ChampIDFusion)

    if len(dicoD.keys()) > 0:
        arcpy.AddMessage("Implementation des " + str(len(dicoD.keys())) + " ID Fusion lies aux surfaces DSCGR: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        ImplementationGroupSID(dicoSD, Couche, ChampIDSentinel, ChampIDFusion)

    if len(dicoSent.keys()) > 0:
        arcpy.AddMessage("Implementation des " + str(len(dicoSent.keys())) + " ID Fusion des surfaces Sentinel liees entre elles: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        dicoSSent = InversionDicoRef(dicoSent)
        ImplementationGroupSID(dicoSSent, Couche, ChampIDSentinel, ChampIDFusion)

    arcpy.AddMessage("Pour toutes les autres Sentinel n'appartenant pas a un groupe Champ Num_S est recupere sur ID_Fusion: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    uCurs = arcpy.da.UpdateCursor(Couche, ["Num_S", ChampIDFusion], ChampIDFusion + " IS NULL")
    for u in uCurs:
         u[1] = u[0]
         uCurs.updateRow(u)
    del uCurs
    arcpy.Delete_management(Couche)
arcpy.AddMessage("Fin du processus: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# ------------------------------------Fusion----------------------------------

CoucheDissolve = Couche + "_Dissolved"
arcpy.Dissolve_management(Couche, CoucheDissolve, "ID_Fusion_" + str(seuil) + "j", [["date_date", "MIN"], ["date_date", "MAX"]])

# -----------------------------Comptage des redétections----------------------

