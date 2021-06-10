# -*- coding: utf8 -*-

# ----------------------------------------------------------------------------------------------
# Script           : Global.py
# Author           : Côme DAVAL
# Date             : 07/04/2021
# Object           : Chaine de traitement complète
# ----------------------------------------------------------------------------------------------
from regroupement import *
from FctArcpy import *
from methodes import *
from reference import *
import sys, os
import arcpy

# from os import chdir
import datetime as dt
import pickle

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
seuilSurface = .6
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

fcIn = Merged_Data
supression_doublons(fcIn, gdb)

# # ------------------------------Aberrations MOS----------------------------------------
# Extraction des catégories MOS utilisées
arcpy.Delete_management(Couche_MOS_Select)
arcpy.Delete_management(Merged_Data_Inter_MOS)
arcpy.Delete_management(Merged_Data_SS_Ab)
arcpy.Select_analysis(Couche_MOS, Couche_MOS_Select, where_clause_mos)
arcpy.TabulateIntersection_analysis(Merged_Data_SS_Doublons, "OBJECTID", Couche_MOS_Select, Merged_Data_Inter_MOS, champ_cat_mos, out_units= "HECTARES",)

# Recuperation des entrees
Layer1 = Merged_Data_SS_Doublons
Tb_Intersect = Merged_Data_Inter_MOS
FieldOIDLayer1 = ObjectID_Org_Layer  
FieldClasse = champ_cat_mos

detection_surface_ab_mos(gdb, Tb_Intersect, Layer1, FieldOIDLayer1, FieldClasse, MinPCT, MinPCTAb)

# # -----------------------------Indice de confiance--------------------------------
arcpy.AddMessage("Debut du processus Indice de confiance : " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

couche = Merged_Data_SS_Ab
coucheTravail = "Merged_Data_Trust"
champs = ["OBJECTID", "Shape@", "liste_overlaps", "count_overlaps", "date_date"]
arcpy.Delete_management(gdb + "/" + coucheTravail)
arcpy.Delete_management(coucheTravail)
arcpy.MakeFeatureLayer_management(gdb + "/" + couche, coucheTravail)
arcpy.Sort_management(coucheTravail, coucheTravail, [datedate_field])
arcpy.AddField_management(coucheTravail, "liste_overlaps", "Text")
arcpy.AddField_management(coucheTravail, "count_overlaps", "Double")

calcul_overlaps(gdb, seuil, seuilSurface, coucheTravail, champs)

# # ------------------------------Références----------------------------------------
arcpy.AddMessage("Debut du processus d'ajout des références : " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
# Ajout des références
l_couches = [Merged_Data_SS_Ab, Couche_DSCGR, Couche_VIIRS, Couche_GROUPE]
# l_couches = [coucheTravail, Couche_DSCGR, Couche_VIIRS, Couche_GROUPE]
list_nature = ["S", "D", "V", "G"]
list_oid = ["OBJECTID"]*4

fcSentinel = Merged_Data_SS_Ab
# fcSentinel = coucheTravail
fcDSCGR = Couche_DSCGR
fcVIIRS = Couche_VIIRS
fcGS = Couche_GROUPE
fieldDate = "date"
Nom_sortie = Fusion_Data  # nom de la couche en sortie
# WoorkIngdb()
dateDebut = str(annee_etude) + '0101'
dateFin = str(annee_etude+1) + '0301'
dateDebutRef = str(annee_etude-1) + '0101'
where_clause = fieldDate + " >= '" + dateDebut + "' AND " + fieldDate + " < '" + dateFin + "'"
where_clause_ref = fieldDate + " >= '" + dateDebutRef + "' AND " + fieldDate + " < '" + dateFin + "'"
arcpy.AddMessage(dateDebut)
arcpy.AddMessage(dateFin)
arcpy.AddMessage(dateDebutRef)

arcpy.Delete_management(Fusion_Data)

creation_id_feux(ListCoucheRef, ListChampsDate, l_couches, list_nature, list_oid)
creation_couche_fusionnee(datedate_field, fcSentinel, fcDSCGR, fcVIIRS, fcGS, fieldDate, Nom_sortie, where_clause, where_clause_ref)

# # ------------------------------REGROUPEMENT ETAPE 1----------------------------------------

arcpy.AddMessage("Debut du processus Regroupement : " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

CoucheTOT = Fusion_Data
CoucheTOT_Buffer = CoucheTOT + "_Buffer"
TableRel = CoucheTOT + "_OverlapsALL" + str(seuil) + "j"
SortedCoucheTOT = CoucheTOT + "_Sorted"
# ChampCoucheTOT = ["Num_S", "Nature", datedate_field, "Shape@", "OBJECTID", "count_overlaps"]
ChampCoucheTOT = ["Num_S", "Nature", datedate_field, "Shape@", "OBJECTID"]
ChampTableRel = ["Num_S", "Nature", datedate_field, "Num_S_1", "Nature_1", datedate_field + "_1", "RelationNature", "Delta"]
ChampIDSentinel = "Num_S"

creation_table_relation(gdb, seuil, buffer, datedate_field, CoucheTOT, CoucheTOT_Buffer, TableRel, SortedCoucheTOT, ChampCoucheTOT, ChampTableRel)

arcpy.AddMessage("Recuperation des informations de la Table de proximite " + TableRel + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

verification_table_rel(TableRel)

arcpy.AddMessage("Fin de l'étape 1 du processus de regroupement: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# # ------------------------------REGROUPEMENT ETAPE 2----------------------------------------

arcpy.AddMessage("Debut du processus Etape 2: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

Couche = Fusion_Data
ChampTableRel = ["Num_S", "Nature", "date_date", "Num_S_1", "Nature_1", "date_date_1", "RelationNature", "Delta"]
ChampIDSentinel = "Num_S"
ChampIDFusion = "ID_Fusion_" + str(seuil) + "j"
TableRel = Fusion_Data + "_OverlapsALL" + str(seuil) + "j"

arcpy.AddMessage("Traitement pour le seuil " + str(seuil) + " jours")
arcpy.AddMessage("Recuperation des informations de la Table de proximite " + TableRel + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


Relations, Sent, Viirs, D, GS = creation_dico(gdb, TableRel, ChampTableRel)

'''CHANGEMENT ORDRE REFERENCE DSCGR puis VIIRS puis Groupe Incendie An-1'''
arcpy.AddMessage("Classification selon DSCGR: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
def calcul_groups(seuil, Relations, Sent, D):
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
    return Sent,dicoD,dicoSD

Sent, dicoD, dicoSD = calcul_groups(seuil, Relations, Sent, D)

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
    file = open("test_regroupement_sent", 'wb')
    pickle.dump([Sent, Relations, seuil], file)
    dicoSent = ClasseOnlySentinel(Sent, Relations, seuil)
    arcpy.AddMessage(str(len(Sent)) + " Sentinels a classer")

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

