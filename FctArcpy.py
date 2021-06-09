# -*- coding: utf8 -*-

#----------------------------------------------------------------------------------------------
# Script           : FctArcpy.py
# Author           : Chloe Bertrand
# Date             : 29/05/2019
# Object           : Fonctions en lien avec Arcpy
#----------------------------------------------------------------------------------------------

########################### IMPORTS ###########################
import arcpy
from arcpy import env
import os
from FctExcel import *
import pickle
########################### FONCTIONS ###########################

def CreateChamp(couche, champ, champType='TEXT',taille =64):
    """
    Fonction qui gere si le champ existe deja ou non avant de le creer
    :param couche: nom de la couche d'entites pour laquelle le champ doit etre ajoute
    :param champ: nom du champ a ajouter
    :param champType: nom du type de champ souhaite ("DOUBLE","TEXT"...)
    :return:
    """
    try:
        arcpy.AddMessage("Renouvellement du Champ {0} dans la couche {1}\n".format(champ, couche))
        arcpy.DeleteField_management(couche, [champ])
    except:
        arcpy.AddMessage("Creation du Champ {0} dans la couche {1}\n".format(champ, couche))
    arcpy.AddField_management(couche, champ, champType, taille)


def CalculSuperficieHa(l_couches):
    """
    Ajout d'un champ contenant la superficie en hectare de chaque polygone
    :param l_couches: liste des couches auquelles ajouter un champ de superficie
    :return:
    """
    for i in range(len(l_couches)):
        couche = l_couches[i]
        CreateChamp(couche, 'SurfaceHa' + l_couches[i].split('\\')[-1][:10], 'DOUBLE')
        arcpy.AddMessage("Calcul du Champ {0} dans la couche {1}\n".format('SurfaceHa' + couche.split('\\')[-1][:10], couche))
        arcpy.CalculateField_management(couche, 'SurfaceHa' + couche.split('\\')[-1][:10], "!shape.area@hectares!", 'PYTHON_9.3')

def WoorkInGDB():
    if arcpy.env.workspace[-4:] != '.gdb':
        if not os.path.exists(arcpy.env.workspace + '\\temp.gdb'):
            arcpy.CreateFileGDB_management(arcpy.env.workspace, 'temp.gdb')
        arcpy.env.workspace += '\\' + 'temp.gdb'

def CalculNbIncSuperficie(coucheInc):
    nb_inc = int(str(arcpy.GetCount_management(coucheInc)))
    sCurs = arcpy.da.SearchCursor(coucheInc, ['SurfaceHa' + coucheInc.split('\\')[-1][:10]])
    # arcpy.AddMessage(sCurs)
    rows = [row[0] for row in sCurs]
    surface_inc = 0
    for row in rows:
        surface_inc += row
    del sCurs
    arcpy.AddMessage("Le nombre d incendie est de {0} et la superficie totale incendiee est de {1} ha\n".format(nb_inc,surface_inc))
    return nb_inc, surface_inc

def RegroupeLigne(couche, champNom, l_couches_temp):
    sCurs = arcpy.da.SearchCursor(couche, [champNom])
    rows = [row for row in sCurs]
    if len(rows) != len(list(set(rows))):
        coucheDissolve = arcpy.env.workspace + '\\' + couche.split('\\')[-1] + "Dissolve"
        arcpy.Dissolve_management(couche, coucheDissolve, [champNom],
                                  [['SurfaceHa' + couche.split('\\')[-1][:10], 'SUM']])
        l_couches_temp.append(coucheDissolve)
        champSurface = 'SUM_SurfaceHa' + couche.split('\\')[-1][:10]
        couche = coucheDissolve
    else:
        coucheDissolve = couche
        champSurface = 'SurfaceHa' + couche.split('\\')[-1][:10]
    del sCurs
    return coucheDissolve, champSurface, couche, l_couches_temp


def TabulateIntersecToRows(couche, champsCouche, coucheIntersec, champsIntersec, l_couches_temp):
    TabulateIntersec = arcpy.env.workspace + '\\TabulateIntersec_' + couche.split('\\')[-1][:10]+ '_' + \
                                        coucheIntersec.split('\\')[-1][:10]
    if os.path.exists(TabulateIntersec):
        arcpy.Delete_management(TabulateIntersec)
    arcpy.AddMessage("\n")
    arcpy.AddMessage(couche)
    arcpy.AddMessage([field.name for field in arcpy.ListFields(couche)])
    arcpy.AddMessage(champsCouche)
    arcpy.AddMessage(coucheIntersec)
    arcpy.AddMessage([field.name for field in arcpy.ListFields(coucheIntersec)])
    arcpy.AddMessage(champsIntersec)
    desc = arcpy.Describe(coucheIntersec)
    if desc.shapeType == 'Multipoint' or desc.shapeType == "Point":
        arcpy.TabulateIntersection_analysis(couche, champsCouche,
                                        coucheIntersec,
                                        TabulateIntersec,
                                        champsIntersec)
    else :
        arcpy.TabulateIntersection_analysis(couche, champsCouche,
                                        coucheIntersec,
                                        TabulateIntersec,
                                        champsIntersec,
                                        out_units='HECTARES')
    if arcpy.GetCount_management(TabulateIntersec)==0:
        arcpy.AddError("Attention la table en sortie d'intersection  et recapitulatif est vide")
    l_couches_temp.append(TabulateIntersec)
    return l_couches_temp, TabulateIntersec


def IntersecToRows(couche1, couche2, l_couches_temp, champNom1, champNom2):
    Intersec = arcpy.env.workspace + '\\Intersec_' + couche1.split('\\')[-1] + '_' + \
               couche2.split('\\')[-1]
    if os.path.exists(Intersec):
        arcpy.Delete_management(Intersec)
    l_couches_temp.append(Intersec)
    arcpy.Intersect_analysis([couche1, couche2], Intersec)

    # Calcul de l'aire en hectares des polygones crees
    CreateChamp(Intersec, 'Surface_Intersec_ha', 'DOUBLE')
    arcpy.CalculateField_management(Intersec, 'Surface_Intersec_ha', "!shape.area@hectares!",
                                    'PYTHON_9.3')

    if champNom2.lower() == champNom1.lower():
        champNom2 = champNom2 + "_1"

    return champNom2, l_couches_temp, Intersec


def ResumeStat(coucheIntersec, l_couches_temp, nomCoucheResume, champsResume1, champsResume2,champsDeb1,champsFin1,champsDeb2,champsFin2,champS, stat='SUM'):
    Resume1 = arcpy.env.workspace + '\\Resume1_' + nomCoucheResume
    l_couches_temp.append(Resume1)
    Resume2 = arcpy.env.workspace + '\\Resume2_' + nomCoucheResume
    l_couches_temp.append(Resume2)
    arcpy.Statistics_analysis(coucheIntersec, Resume1, [[champS, stat]],
                              champsResume1)
    arcpy.Statistics_analysis(Resume1, Resume2, [[stat+"_"+champS, stat]],
                              champsResume2)

    if champsDeb1!="Non":
        sCurs = arcpy.da.SearchCursor(Resume1,
                                      champsDeb1 + ['FREQUENCY', stat + '_' + champS] + champsFin1)
        rows1 = [list(row) for row in sCurs]
        del sCurs
    else :
        rows1 = []

    if champsDeb2 != "Non":
        sCurs = arcpy.da.SearchCursor(Resume2,
                                  champsDeb2 + ['FREQUENCY', stat+"_"+stat+'_'+champS]+champsFin2 )
        rows2 = [list(row) for row in sCurs]
        del sCurs
    else :
        rows2 = []
    return rows1, rows2, l_couches_temp

def ExtractionInfoParZone(workbook,ChampExcelZone, Formules,l_couchesZone,l_champNomZone,l_couches_temp,coucheInc,champNomInc,i):
    # Permet de regrouper les lignes par valeurs identiques
    coucheZone, champSurfaceZone, l_couchesZone[i], l_couches_temp = RegroupeLigne(l_couchesZone[i], l_champNomZone[i],
                                                                                   l_couches_temp)

    # Production des polygones d'intersection entre les surfaces incendiees et les entitees environnementales
    champNomInc2, l_couches_temp, IntersecZone_name = IntersecToRows(coucheZone, coucheInc, l_couches_temp,
                                                                     l_champNomZone[i], champNomInc)

    # Resume des informations par entitee environnementale
    rows1, rows, l_couches_temp = ResumeStat(IntersecZone_name, l_couches_temp, coucheZone.split('\\')[-1],
                                             [l_champNomZone[i], champNomInc2, champSurfaceZone],
                                             [l_champNomZone[i], champSurfaceZone], "Non", [],
                                             [l_champNomZone[i]], [champSurfaceZone], 'Surface_Intersec_ha')

    # Si les donnees environnementales ne croisent pas d'incendie ce n'est pas la peine de continuer
    if len(rows) > 0:
        # Ajout des informations extraites dans le fichier Excel
        sheetName = coucheZone.split('\\')[-1][:30].encode('ascii', 'ignore')
        Add_to_excel(workbook, sheetName, ChampExcelZone, Formules, rows)
        for k in range(len(ChampExcelZone) - 1):
            Add_Chart(workbook, sheetName, len(ChampExcelZone) + 2, k * 20 + 1, len(rows),
                      [k + 1], 0,
                      ChampExcelZone[k + 1]['header'] + ' pour ' + coucheZone.split('\\')[-1],
                      ChampExcelZone[k + 1]['header'])
    return rows, coucheZone, champSurfaceZone, l_couchesZone, l_couches_temp, IntersecZone_name

def ExtractionInfoParAdmiZone(workbook,ChampExcelAdmiZone, FormulesTout,l_couchesAdmi,l_champNomZone,l_couches_temp,champNomInc,coucheZone, champSurfaceZone,l_champNomAdmi,IntersecZone_name,i):
    coucheAdmi, champSurfaceAdmi, l_couchesAdmi[i], l_couches_temp = RegroupeLigne(l_couchesAdmi[i], l_champNomAdmi[i],
                                                                                   l_couches_temp)
    # Production d'une table d'interseciton entre les surfaces brulees par zone environnementale avec les zones administratives
    l_couches_temp, TabulateIntersec_name = TabulateIntersecToRows(IntersecZone_name,
                                                                   [l_champNomZone[i], champSurfaceZone, champNomInc],
                                                                   coucheAdmi, [l_champNomAdmi[i], champSurfaceAdmi],
                                                                   l_couches_temp)
    # On prend en compte que le champ nom de la couche zone peut être identique à celui de la couche administrative
    if l_champNomZone[i].lower() == l_champNomAdmi[i].lower():
        champNomAdmi = l_champNomAdmi[i] + "_1"
    else:
        champNomAdmi = l_champNomAdmi[i]
    # Resume des informations par entitees administratives et environnementales
    desc = arcpy.Describe(coucheAdmi)
    if desc.shapeType == 'Multipoint' or desc.shapeType == "Point":
        stat = "COUNT"
        champStat = champNomAdmi
    else :
        stat = "SUM"
        champStat = 'AREA'

    rows1, rows, l_couches_temp = ResumeStat(TabulateIntersec_name, l_couches_temp,
                                             coucheZone.split('\\')[-1] + '_' + coucheAdmi.split('\\')[-1],
                                             [l_champNomZone[i], champNomAdmi, champNomInc, champSurfaceAdmi,
                                              champSurfaceZone],
                                             [l_champNomZone[i], champNomAdmi, champSurfaceAdmi, champSurfaceZone],
                                             "Non",
                                             [], [champNomAdmi, l_champNomZone[i]], [champSurfaceAdmi,
                                                                                     champSurfaceZone], champStat, stat)
    if len(rows) > 0:
        if desc.shapeType == 'Multipoint' or desc.shapeType == "Point":
            FormulesTout = FormulesTout[:-3]
            arcpy.AddMessage((rows))
            for i in range(len(rows)):
                rows[i] = rows[i][:3]
            ChampExcelAdmiZone = ChampExcelAdmiZone[:3]+ChampExcelAdmiZone[6:-3]
        # Ajout des informations extraites dans le fichier Excel
        excel_name = coucheAdmi.split('\\')[-1][:10] + '_' + coucheZone.split('\\')[-1][:10]
        Add_to_excel(workbook, excel_name[:30], ChampExcelAdmiZone,
                     FormulesTout, rows)
    return l_couches_temp


def add_field_Nature_Num(couche, nature, fieldOID):
    # creation des champs  Nature et Num_S pour ne pas perdre l'origine de la couche et les identifiants avant fusion
    CreateChamp(couche, "Nature")
    CreateChamp(couche, "Num_S")
    arcpy.CalculateField_management(couche, "Nature", "'" + nature + "'", "PYTHON_9.3")
    arcpy.CalculateField_management(couche, "Num_S", "!Nature![0] + str(!" + fieldOID + "!)",
                                        "PYTHON_9.3")

def SaveDicoInFile(chemin, dico):
    f = open(chemin, "wb")
    p = pickle.Pickler(f)
    p.dump(dico)
    f.close()

def ExtractDico(chemin):
    f = open(chemin,"rb")
    p = pickle.Unpickler(f)
    dico = p.load()
    f.close()
    return dico

