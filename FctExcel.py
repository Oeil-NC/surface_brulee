# -*- coding: utf8 -*-

#----------------------------------------------------------------------------------------------
# Script           : FctExcel.py
# Author           : Chloe Bertrand
# Date             : 29/05/2019
# Object           : Fonctions en lien avec Excel
#----------------------------------------------------------------------------------------------

########################### IMPORTS ###########################
import arcpy
from datetime import *
import os
import xlsxwriter as xls
from arcpy import env

########################### FONCTIONS ###########################

def OuvertureFichierExcel():
    # ouverture du fichier excel
    arcpy.AddMessage("Creation du fichier Excel\n")
    dossier_excel = ""
    if arcpy.env.workspace.split(os.path.sep)[-1][-4:] != ".gdb":
        dossier_excel = arcpy.env.workspace
    else:
        for i in range(len(arcpy.env.workspace.split(os.path.sep)) - 1):
            dossier_excel += arcpy.env.workspace.split(os.path.sep)[i] + os.path.sep
    if not os.path.exists(dossier_excel + "fichiersExcel"):
        os.makedirs(dossier_excel + "fichiersExcel")
    workbook = xls.Workbook(dossier_excel + "fichiersExcel" + os.path.sep + fichierExcel + '.xlsx',
                            {'default_date_format': 'dd/mm/yyyy'})
    return workbook

def Add_to_excel(workbook, sheetName, champExcel, formules, rows, position=[0, 0]):
    """
    Ajout des tables et de leur mise en forme dans un fichier excel
    :param workbook: fichier excel d'interet
    :param sheetName: feuille excel d'interet
    :param champExcel: liste des noms des entetes de la table en sortie
    :param formules: liste des formules excel utilisees
    :param rows: liste des informations en lignes a rentrer dans la table
    :return:
    """
    sheetName = sheetName.encode('ascii', 'ignore')
    arcpy.AddMessage("Ecriture de la feuille excel {0}".format(sheetName.encode('ascii', 'ignore')))
    if sheetName in [worksheet.get_name() for worksheet in workbook.worksheets()]:
        worksheet = workbook.get_worksheet_by_name(sheetName)
    else:
        worksheet = workbook.add_worksheet(sheetName)
    for i in range(len(rows)):
        # arcpy.AddMessage(rows[i])
        worksheet.write_row(xls.utility.xl_col_to_name(position[0]) + str(i + 2 + position[1]), rows[i])
        for j in range(len(formules)):
            formule = formules[j].replace('ICI', str(i + 2 + position[1]))
            #arcpy.AddMessage( formule)
            worksheet.write_formula(
                xls.utility.xl_col_to_name(len(rows[i]) + j + position[0]) + str(i + 2 + position[1]), formule)
    worksheet.add_table(
        xls.utility.xl_col_to_name(position[0]) + str(position[1] + 1) + ':' + xls.utility.xl_col_to_name(
            len(champExcel) - 1 + position[0]) + str(len(rows) + 1 + position[1]), {'columns': champExcel})


def Add_Chart(workbook,  sheetName, num_c, num_l, len_rows, values_col, categorie_col, title, ytitle, graphType=None,value_lgn=0, categorie_lgn=0):
    """
    Ajout des graphiques pour les Zones environnementales et administratives
    :param workbook: fichier excel
    :param worksheet: feuille excel dans laquelle sera positionne le graphique
    :param sheetName: nom de la feuille excel contenant les donnees
    :param num_c: numero de la colonne d'insertion du graphique
    :param num_l: numero de la ligne d'insertion du graphique
    :param len_rows: longueur des donnees
    :param value_col: colonne des valeurs
    :param categorie_col: colonne des categories
    :param title: titre du graphique
    :param ytitle: titre de l'ordonnee
    :return:
    """
    arcpy.AddMessage("Creation du graphique {0}".format(title.encode('ascii', 'ignore')))
    worksheet = workbook.get_worksheet_by_name(sheetName)
    dico = {'categories': "='" + sheetName + "'!" + xls.utility.xl_col_to_name(categorie_col) + str(
        categorie_lgn + 2) + ':' + xls.utility.xl_col_to_name(categorie_col) + str(categorie_lgn + len_rows + 1),'name':'Total'}
    if graphType!=None and graphType != 'line':
        chart = workbook.add_chart({'type': graphType})
        dico['data_labels']={'value': True}
    elif len_rows <= 20:
        chart = workbook.add_chart({'type': 'column'})
        dico['data_labels'] = {'value': False}
        chart.set_table()
    else:
        chart = workbook.add_chart({'type': 'radar'})
        dico['data_labels'] = {'value': False}

    if graphType == 'line':
        chart = workbook.add_chart({'type': graphType})
        dico['marker'] = {'type': 'diamond'}
        chart.set_table()

    # arcpy.AddMessage('=' + sheetName + '!' + value_col + '2:' + value_col + str(len_rows + 1))
    for i in range(len(values_col)):
        dico['values']="='" + sheetName + "'!" + xls.utility.xl_col_to_name(values_col[i]) + str(value_lgn+2)+':' + xls.utility.xl_col_to_name(values_col[i]) + str(value_lgn+len_rows + 1)
        if len(values_col) > 1:
            dico['name'] = [sheetName, value_lgn, values_col[i]]

            print(dico['name'])
        chart.add_series(dico)
    chart.set_title({'name': title})
    chart.set_y_axis({'name': ytitle})
    worksheet.insert_chart(xls.utility.xl_col_to_name(num_c) + str(num_l), chart)
