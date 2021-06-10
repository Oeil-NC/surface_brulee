import os
from urllib.request import quote, unquote

import arcpy

### -- Fonctions du module 3 Aberrations MOS --

def DicoTableInters(sCurs, FieldClasse, fcIn, fieldsAberrant, MinPCTAb, MinPCT):
    dico = {}
    for row in sCurs:
        OIDC1 = int(row[0])  # Enregistrement de la cle du dictionnaire
        FCtype = [str(field.type) for field in arcpy.ListFields(fcIn) if field.name == FieldClasse][0]
        # Si c'est la premiere fois que l'on rencontre l'identifiant de la couche dans la table
        # On initialise les variables
        if OIDC1 not in dico:
            dico[OIDC1] = ["", "", "", "", 0.00, ""]

        # Si le pourcentage de la classe est superieur a celui minimal tolere
        if round(row[2], 2) >= MinPCT:
            Classe = row[1] + ";"
            Perc = str(round(row[2], 2)).replace(".", ",") + "%;"
            # On enregistre le champ CLASSE et le pourcentage du champ CLASSE
            dico[OIDC1][0] += Classe
            dico[OIDC1][1] += Perc

            # Si la Classe correspond à un champ aberrant
            if str(unquote(quote(row[1].encode('utf-8')))).replace("'", "") in fieldsAberrant:
                dico[OIDC1][2] += Classe
                dico[OIDC1][3] += Perc
                dico[OIDC1][4] += round(row[2], 2)
                # Si la somme des pourcentages aberrant est superieure au pourcentage minimal tolere
                if dico[OIDC1][4] >= MinPCTAb:
                    dico[OIDC1][5] = u"Pourcentage Aberrant superieur a  " + u"" + str(MinPCTAb).replace(".", ",")

    arcpy.AddMessage(dico)
    del sCurs
    return dico


def recup_oid(tab):
    foid = [str(f.name) for f in arcpy.ListFields(tab) if f.type == "OID"]
    try:
        return foid[0]
    except:
        return ""


def AddValToRow(liste):
    # Les ';' finaux sont supprimes et les valeurs ajoutes aux lignes
    try:
        return liste.replace("'", u"\u2019")[:-1]
    except:
        return ""

def CreateChamps(Layer1, dico, Champs):
    # Calcul de longueur des champs
    MaxCl = max([len(cl[0]) for cl in dico.values()])
    MaxPct = max([len(pct[1]) for pct in dico.values()])

    arcpy.AddMessage("\nAjout des champs de sortie dans la couche d'entree")
    for i in range(len(Champs)):
        # On supprime les champs de sortie si ils existent deja
        arcpy.DeleteField_management(Layer1, Champs[i])
    # On cree les champs de sortie
    arcpy.AddField_management(Layer1, Champs[0], 'TEXT', field_length=MaxCl + 2)
    arcpy.AddField_management(Layer1, Champs[2], 'TEXT', field_length=MaxCl + 2)
    arcpy.AddField_management(Layer1, Champs[1], "TEXT", field_length=MaxPct + 2)
    arcpy.AddField_management(Layer1, Champs[3], "TEXT", field_length=MaxPct + 2)
    arcpy.AddField_management(Layer1, Champs[4], "TEXT")
    arcpy.AddField_management(Layer1, Champs[5], "TEXT")


def update_layer1(uCurs, dico):
    for row in uCurs:
        oidc1 = int(row[0])
        if oidc1 in dico:
            for i in range(4):
                row[i + 1] = AddValToRow(dico[oidc1][i])

            try:
                row[5] = u"" + str(dico[oidc1][4]).replace(".", ",") + "%"
            except:
                pass

            row[6] = dico[oidc1][5]
            # Mise a jour des informations

            # arcpy.AddMessage("\n\ndico {0}".format(dico[oidc1]))
            # arcpy.AddMessage("row {0}".format(row))
            uCurs.updateRow(row)

        else:
            arcpy.AddMessage("pas de classe !!!!!!!!" + str(row[0]))

    del uCurs

def detection_surface_ab_mos(gdb, Tb_Intersect, Layer1, FieldOIDLayer1, FieldClasse, MinPCT, MinPCTAb):
    FieldPercentage = "PERCENTAGE"
    SortieChampClasse = "CLASSE"
    SortieChampPCT = "PERCENTAGE"

    fieldsAberrant = ['Eaux maritimes',
                'Mines, décharges minières, infrastructures et chantiers miniers',
                'Plages, dunes et sable', 'Plages, dunes, sable', 'Roches et sols nus',
                'Réseaux de communication', 'Tissu urbain continu', 'Tissu urbain discontinu',
                'Zones humides intérieures', 'Zones industrielles ou commerciales et équipements']

    SortieChampClasseAb = "CLASSE_Ab"
    SortieChampPCTAb = "PERCENTAGE_Ab"
    SortieChampSommeAb = "SUM_PERCENTAGE_Ab"

    # arcpy.AddMessage("recuperation des champs ID de la couche et de la table")
    FieldOIDTb = recup_oid(Tb_Intersect)
    FieldOIDC1 = recup_oid(Layer1)

    # Dictionnaire pour lequel les cles correspondent aux IDs de la couche en entrée
    # au quelles sont associees des listes contenant la liste des noms de Classe,
    # la liste des pourcentages associees, la liste des classes aberrantes,
    # la liste des pourcentages associees, la somme des pourcentages des
    # champs aberrants, et la mention de supression

    sCurs = arcpy.da.SearchCursor(Tb_Intersect, [FieldOIDLayer1, FieldClasse, FieldPercentage],
                                    where_clause=FieldPercentage + " >= " + str(MinPCT),
                                    sql_clause=(None, "ORDER BY " + FieldOIDTb))
    dico = DicoTableInters(sCurs, FieldClasse, Tb_Intersect, fieldsAberrant, MinPCTAb, MinPCT)

    # On s'occupe des champs de sortie de la couche d'entree
    Champs = [SortieChampClasse, SortieChampPCT, SortieChampClasseAb, SortieChampPCTAb, SortieChampSommeAb, 'A_SUPPRIMER']
    CreateChamps(Layer1, dico, Champs)

    uCurs = arcpy.da.UpdateCursor(Layer1,
                                    [FieldOIDC1, SortieChampClasse, SortieChampPCT, SortieChampClasseAb, SortieChampPCTAb,
                                    SortieChampSommeAb, 'A_SUPPRIMER'], sql_clause=(None, "ORDER BY " + FieldOIDC1))
    update_layer1(uCurs, dico)

    # Creation d'une couche d'entites sans aberrations
    arcpy.MakeFeatureLayer_management(Layer1, 'Layer1',"A_SUPPRIMER IS NULL OR A_SUPPRIMER LIKE ''")
    arcpy.CopyFeatures_management('Layer1', gdb + os.path.sep + Layer1.split('\\')[-1] + "_SansAb")
    arcpy.Delete_management('Layer1')
