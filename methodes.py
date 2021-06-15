import datetime as dt

import arcpy

# # ------------------------------FONCTIONS-----------------------------------------------------


def calcul_overlaps(gdb, seuil, seuilSurface, coucheTravail, champs):
    sCurs1 = [list(i) for i in arcpy.da.SearchCursor(coucheTravail, champs)]
    sCurs2 = [i for i in sCurs1]
    sCurs1.pop()
    sCurs2.pop(0)
    dico = {}
    l = len(sCurs1)
    for index, s1 in enumerate(sCurs1):
        dico[s1[0]] = []
        if index%100 == 0:
            arcpy.AddMessage('{:.1f}% analysé'.format(index/l*100))
        for s2 in sCurs2:
            if (s2[4] - s1[4]).days > seuil:
                break
            if s1[1].disjoint(s2[1]):
                continue
            s_inter = s1[1].intersect(s2[1], 4)
            area = s_inter.getArea("GEODESIC", "SQUAREMETERS")
            area_org = s1[1].getArea("GEODESIC", "SQUAREMETERS")
            rap = area/area_org
            if rap >= seuilSurface:
                dico[s1[0]].append([s2[0], area, rap])  
        sCurs2.pop(0)
    # arcpy.AddMessage(dico)

    uCurs = arcpy.da.UpdateCursor(coucheTravail, champs)
    for u in uCurs:
        if u[0] in dico.keys() and dico[u[0]] != []:
            u[2] = ''
            u[3] = 0
            for ol in dico[u[0]]:
                try:
                    u[2] += str(ol[0]) + ', '
                    u[3] += 1
                except TypeError:
                    u[3] += 1
                    pass
            try:
                uCurs.updateRow(u)
            except RuntimeError:
                arcpy.AddMessage("Valeur invalide")
                u[2] = "Invalide"
                uCurs.updateRow(u)
    try:
        arcpy.CopyFeatures_management(coucheTravail, gdb + "/" + coucheTravail)
    except :
        arcpy.Delete_management(gdb + "/" + coucheTravail)
        arcpy.CopyFeatures_management(coucheTravail, gdb + "/" + coucheTravail)

### -- Fonctions du module 5 Regroupement --
def RelationDouble(Relats, ChampTBRel):
    nbch = len(ChampTBRel)
    inumS = ChampTBRel.index("Num_S")
    inumS1 = ChampTBRel.index("Num_S_1")
    arcpy.AddMessage("Relation double a supprimer sur les relations dans la table concernee")
    #initialisation du traitement a 0
    RelatsDb = [db for db in Relats]
    for dp in Relats:
        i = Relats.index(dp)
        Relats[i].append(0)
    nbdep = len(RelatsDb)
    arcpy.AddMessage(str(nbdep) + " relations en entree")
    for dpt in Relats:
        y = Relats.index(dpt)
        if dpt[nbch] == 0:
            RelatsDbSel = [db for db in RelatsDb if dpt[inumS] == db[inumS1] and dpt[inumS1] == db[inumS]]
            Relats[y][nbch] = 1
            if len(RelatsDbSel) > 0:
                RelatsDbSel = RelatsDbSel[0]
                RelatsDb.remove(RelatsDbSel)
                yi = Relats.index(RelatsDbSel)
                Relats[yi][nbch] = 1
    nbfin = len(RelatsDb)
    arcpy.AddMessage(str(nbfin) + " relations en sortie")
    return RelatsDb

###Fonction qui associe les premiers feux de reference avec les sentinels directs
def RefSentinel(VIIRS, Sentinels, Rels, CodeRef, Seuil):
    SentinelsTraites = dict()
    SentinelsNonTraites = [s for s in Sentinels]
    # dictionnaire cle = Sentinel valeur = liste(VIIRSid, Delta)
    # arcpy.AddMessage(SentinelsTraites)
    dicoREF = dict()
    for v in VIIRS:
        if v not in dicoREF.keys():
            dicoREF[v] = list()
        VSR = [rel for rel in Rels if rel[6] == CodeRef + " - S" and rel[0] == v and rel[7] <= Seuil and rel[7] >= 0]
        if len(VSR) > 0:
            for vsr in VSR:
                if vsr[3] in SentinelsNonTraites:
                    dicoREF[v].append(vsr[3])
                    SentinelsTraites[vsr[3]] = [v, vsr[7]]
                    SentinelsNonTraites.remove(vsr[3])
                elif vsr[3] in SentinelsTraites.keys():
                    if vsr[7] < SentinelsTraites[vsr[3]][1]:
                        oldViirs = SentinelsTraites[vsr[3]][0]
                        dicoREF[oldViirs].remove(vsr[3])
                        SentinelsTraites[vsr[3]] = [v,vsr[7]]
                        dicoREF[v].append(vsr[3])
        SVR = [rel for rel in Rels if rel[6] == "S - " + CodeRef and rel[3] == v and rel[7] <= Seuil]
        if len(SVR) > 0:
            for svr in SVR:
                if svr[0] in SentinelsNonTraites:
                    dicoREF[v].append(svr[0])
                    SentinelsTraites[svr[0]] = [v, svr[7]]
                    SentinelsNonTraites.remove(svr[0])
                elif svr[0] in SentinelsTraites.keys():
                    if svr[7] < SentinelsTraites[svr[0]][1]:
                        oldViirs = SentinelsTraites[svr[0]][0]
                        dicoREF[oldViirs].remove(svr[0])
                        SentinelsTraites[svr[0]] = [v, svr[7]]
                        dicoREF[v].append(svr[0])
    arcpy.AddMessage(str(len(dicoREF.keys())) + " groupes issus de " + CodeRef + ": " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    arcpy.AddMessage(str(len(SentinelsTraites.keys())) + " Sentinels classes pour " + CodeRef)
    arcpy.AddMessage(str(len(SentinelsNonTraites)) + " Sentinels non traites")
    return [dicoREF, SentinelsNonTraites]

###en cle les sentinels et en valeur les id de feu de reference
def InversionDicoRef(dicoRef):
    dicoSRef = dict()
    for kd in dicoRef.keys():
        for s in dicoRef[kd]:
            dicoSRef[s] = kd
    return dicoSRef

###Associe les Sentinels intersectant les autres sentinels deja associes a une surface brulee de reference
# Réécrire en itératif pour éviter le problème de récursion

def getDateRef(id, Rels):
    srefvRelD = list()
    for r in Rels:
        if r[0] == id:
            srefvRelD.append(r[2])
            break
        elif r[3] == id:
            srefvRelD.append(r[5])
            break
    # Ajout de date de reference VIIRS pour verifier que tout est classé apres le feu de référence
    DateRef = srefvRelD[0]
    return DateRef

def getRels(id, dateRef, table, seuil, SNT):
    Slies = list()
    for r in table:
        if r[6] == "S1 - S2" or r[6] == "S2 - S1":
            if r[0] == id and r[7] <= seuil and r[5] >= dateRef:
                if r[3] in SNT:
                    Slies.append(r[3])
            elif r[3] == id and r[7] <= seuil and r[2] >= dateRef:
                if r[0] in SNT:
                    Slies.append(r[0])
    Slies = list(set(Slies))
    return Slies

def SentinelSecondaire(dicoRef, Rels, seuil, SNT):
    sent_traite = {}
    for index, key in enumerate(dicoRef.keys()):
        print("{} références analysées, soit {:.0f}%".format(index, index/len(dicoRef.keys())*100))
        liste = dicoRef[key]
        liste_travail = []
        date = getDateRef(key, Rels)
        while len(liste) > 0:
            feu = liste.pop(0)
            enfants = getRels(feu, date, Rels, seuil, SNT)
            for f in enfants:
                SNT.remove(f)
            liste.extend(enfants)
            liste_travail.append(feu)
        sent_traite[key] = liste_travail
        print("{} enfants pour {}".format(len(liste_travail), key))
    return [sent_traite, SNT]

###Regroupement des sentinels entre eux
'''Liste des Sentinels Traites
chaque sentinel non traite dans Sentinel Non Traites
Relations1 = Toutes les relations liees au sentinel concern� en premier element S1 - S2
On recupere les autres sentinels lies au sentinel concerne sur Relations1
Relations2 = Toutes les reations liees au sentinel concern� en second element S1 - S2
On recupere les autres sentinels lies au sentinel concerne sur Relations2
SentinelsLies = On mixte tous les sentinels liées au sentinel concerne
On verifie que dans SentinelsLies il n'y a pas le sentinel concerne
On verifie que dans SentinelsLies il ne s'agit pas de sentinels deja traites
Si SentinelsLies n'est pas vide alors on execute:
    on reexecute RegroupementSentinel sur chaque sentinel lie pour retrouver les autres sentinels qui peuvent etre lies a leur tour
    on recupere en 0 les sentinels non traites, en 1 les sentinels deja traites
Retour des Sentinels Non traites en 0 et Sentinels Traites en 1
'''
def get_relation_sentinel(snt, Rels, ST=None):
    if ST == None:
        ST = list(snt)
    Rel1 = [sr for sr in Rels if sr[0] == snt and sr[4] >= sr[1]]  # On récupère les relation du sentinel avec d'autre sentinel sens 1
    slies1 = [r1[3] for r1 in Rel1]  # Liste des idSentinel liés
    Rel2 = [sr for sr in Rels if sr[3] == snt and sr[1] >= sr[4]]  # On récupère les relation du sentinel avec d'autre sentinel sens 2
    slies2 = [r2[0] for r2 in Rel2]  # -
    slies = list()
    slies.extend(slies1)
    slies.extend(slies2)
     # On vérifie que l'id à traiter n'est pas dans la liste de rels
    ''' Supposition Rels (relations) deja traitees on retire de Rels'''
    Rels = [sr for sr in Rels if sr not in Rel1]  # On supprime les relations traitées de la table de relations (locale)
    Rels = [sr for sr in Rels if sr not in Rel2]  # -
    del slies1, slies2, Rel1, Rel2
    slies = [sl for sl in slies if sl not in ST]
    return slies

def RegroupementSentinelV2(snt, SNT, Rels):
    """ Version itérative de regroupement sentinel
    Cette fonction retourne une liste de feux contenant le feu snt et toutes ses relations :
    enfants
    petit-enfants
    ...
    Ainsi que la liste des feux non traités mise à jour.
    """
    sentinel_groupee = list()
    if snt in SNT:  # On vérifie que le feu n'a pas été traité
        SNT.remove(snt)
        sentinel_groupee.append(snt)
        liste_ref = get_relation_sentinel(snt, Rels)
        while len(liste_ref) > 0:
            feu_enfant = liste_ref.pop(0)
            # On ajoute les feux enfants à la liste à retourner
            if feu_enfant not in sentinel_groupee:
                sentinel_groupee.append(feu_enfant)
            SNT.remove(feu_enfant)
            # On récupère les relations du feu enfant ne concernant pas les feux déjà remontés
            liste_petits_enfants = get_relation_sentinel(feu_enfant, Rels, liste_ref)
            # On ajoute au bout les nouvelles relations trouvées
            liste_ref.extend(liste_petits_enfants)
    return [SNT, sentinel_groupee]

def RegroupementSentinel(snt, SNT, SR):
    """ Version récursive de regroupement sentinel
    Ne pas utiliser
    """
    ST = list()
    if snt in SNT:  # Si le sentinel n'a pas été traité
        ST.append(snt)
        SNT.remove(snt)
        slies = get_relation_sentinel(snt, SR, ST)
        if len(slies) > 0:
            slies = list(set(slies))  # Supprime les doublons
            for sl in slies:
                RS = RegroupementSentinel(sl, SNT, SR)
                SNT = RS[0]
                ST.extend(RS[1])
    SNT = [sntr for sntr in SNT if sntr not in ST]
    return [SNT, ST]
###En Classement des Sentinels sans reference par groupe en s'aidant de la fonction precedente RegroupementSentinel

'''Dictionnaire cree GroupS 
on recupere les relations entre les Sentinels SR qui correspondent aux Seuils
X correspond a l'ID + SGROUP
tant que SentinelsNonTraites n'est pas vide on execute
On envoit vers RegroupementSentinel(premier sentinel de non traites, SentinelNonTraites, Relations entre Sentinel)
Il retourne en 0 = SentinelsNonTraites, en 1 = Sentinels traites ou classes dans les groupes
'''

def ClasseOnlySentinel(Sentinels, Rels, Seuil):
    GroupS = dict()
    SentinelsNonTraites = [s for s in Sentinels]
    SR = [rel for rel in Rels if rel[6] == "S1 - S2" and rel[7] <= Seuil or rel[6] == "S2 - S1" and rel[7] <= Seuil and rel[7] >= 0]
    arcpy.AddMessage("SentinelsNT = " + str(len(SentinelsNonTraites)))
    x = 0
    nb = len(SentinelsNonTraites)
    while nb != 0:
        arcpy.AddMessage(SentinelsNonTraites[0])
        RegSentinel = RegroupementSentinel(SentinelsNonTraites[0], SentinelsNonTraites, SR)
        SentinelsNonTraites = RegSentinel[0]
        SentinelsTraites = RegSentinel[1]
        # Création d'un ID de groupe
        nx = "SGroup_" + str(Seuil) +  "j_" + str(x)
        arcpy.AddMessage(nx)
        arcpy.AddMessage(SentinelsTraites)
        GroupS[nx] = SentinelsTraites
        x += 1
        nb = len(SentinelsNonTraites)
        # SentinelsTraites = list()

    arcpy.AddMessage(str(len(GroupS.keys())) + " groupes issus de Sentinels seulement: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    return GroupS

def PourcentageTraitementBis(ind, nb):
    pc = round(ind/nb*100)
    arcpy.AddMessage("Traitement " + str(pc) + "%: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

###Implementation des identifiants de Groupe Sentinel pour la fusion
def ImplementationGroupSID(dicoS, FeatureLayer, FieldID, FieldFusion):
    nbCles = len(dicoS.keys())
    for ik, kd in enumerate(dicoS.keys()):
        if ik%100 == 0:
            PourcentageTraitementBis(ik, nbCles)
        uCurs = arcpy.da.UpdateCursor(FeatureLayer, [FieldID, FieldFusion], FieldID + " = '" + kd + "'")
        for u in uCurs:
            u[1] = dicoS[kd]
            uCurs.updateRow(u)
        del uCurs

arcpy.AddMessage("Debut du processus: " + dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

###Pour ordonner les Sentinels restants dans l'ordre croissant selon leur date
def OrdonnerSentinel(Sentinels, Relats):
    SentDate = list()
    for s in Sentinels:
        dtS = [rl[2] for rl in Relats if rl[0] == s]
        dtS.extend([rl[5] for rl in Relats if rl[3] == s])
        dtS = list(set(dtS))
        dt = dtS[0]
        SentDate.append((s,dt))
    SentDateOrder = sorted(SentDate,key=lambda sd: sd[1])
    SentiNew = [st[0] for st in SentDateOrder]
    return SentiNew

def calcul_indice_confiance(gdb, couche, datedate_field, seuil_temp, seuil_spat):

    coucheTravail = couche + "_trust_indice"
    champs = ["OBJECTID", "Shape@", "liste_overlaps", "count_overlaps", "date_date"]  

    arcpy.Delete_management(gdb + "/" + coucheTravail)
    arcpy.Delete_management(coucheTravail)
    arcpy.MakeFeatureLayer_management(gdb + "/" + couche, couche)
    arcpy.Sort_management(couche, gdb + "/" + coucheTravail, [datedate_field])
    arcpy.MakeFeatureLayer_management(gdb + "/" + coucheTravail, coucheTravail)
    arcpy.AddField_management(coucheTravail, "liste_overlaps", "Text")
    arcpy.AddField_management(coucheTravail, "count_overlaps", "Double")
    sCurs1 = [list(i) for i in arcpy.da.SearchCursor(coucheTravail, champs)]
    sCurs2 = [i for i in sCurs1]
    sCurs1.pop()
    sCurs2.pop(0)
    dico = {}
    l = len(sCurs1)
    for index, s1 in enumerate(sCurs1):
        dico[s1[0]] = []
        if index%100 == 0:
            arcpy.AddMessage('{:.1f}% analysé'.format(index/l*100))
        for s2 in sCurs2:
            if (s2[4] - s1[4]).days > seuil_temp:
                break
            if s1[1].disjoint(s2[1]):
                continue
            s_inter = s1[1].intersect(s2[1], 4)
            area = s_inter.getArea("GEODESIC", "SQUAREMETERS")
            area_org = s1[1].getArea("GEODESIC", "SQUAREMETERS")
            rap = area/area_org
            if rap >= seuil_spat:
                dico[s1[0]].append([s2[0], area, rap])  
        sCurs2.pop(0)
        # arcpy.AddMessage(dico)

    uCurs = arcpy.da.UpdateCursor(coucheTravail, champs)
    for u in uCurs:
        if u[0] in dico.keys() and dico[u[0]] != []:
            u[2] = ''
            u[3] = 0
            for ol in dico[u[0]]:
                try:
                    u[2] += str(ol[0]) + ', '
                    u[3] += 1
                except TypeError:
                    u[3] += 1
                    pass
            try:
                uCurs.updateRow(u)
            except RuntimeError:
                arcpy.AddMessage("Valeur invalide")
                u[2] = "Invalide"
                uCurs.updateRow(u)
    arcpy.CopyFeatures_management(coucheTravail, gdb + "/" + coucheTravail + "_Final")
    
def nettoyage_fusion_data(couche, ChampIDFusion, NumS, fields, dbt_etude):
    liste_id_fusion = [list(l) for l in arcpy.da.SearchCursor(couche, fields, where_clause=ChampIDFusion + " = " + NumS)]
    liste_a_supp = []
    for feu_ref in liste_id_fusion:
        if feu_ref[2] < dbt_etude:
            liste_a_supp.append(feu_ref[0])
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