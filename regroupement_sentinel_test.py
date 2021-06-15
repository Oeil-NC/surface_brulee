import arcpy
import pickle
import datetime as dt


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
            try:
                SNT.remove(feu_enfant)
            except ValueError:
                print(feu_enfant + " n'est pas dans SNT")
            # On récupère les relations du feu enfant ne concernant pas les feux déjà remontés
            liste_petits_enfants = get_relation_sentinel(feu_enfant, Rels, liste_ref)
            liste_petits_enfants = [l for l in liste_petits_enfants if l in SNT]
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


def ClasseOnlySentinelV2(Sentinels, Rels, Seuil):
    GroupS = dict()
    SentinelsNonTraites = [s for s in Sentinels]
    SR = [rel for rel in Rels if rel[6] == "S1 - S2" and rel[7] <= Seuil or rel[6] == "S2 - S1" and rel[7] <= Seuil and rel[7] >= 0]
    arcpy.AddMessage("SentinelsNT = " + str(len(SentinelsNonTraites)))
    x = 0
    nb = len(SentinelsNonTraites)
    while nb != 0:
        arcpy.AddMessage(SentinelsNonTraites[0])
        RegSentinel = RegroupementSentinelV2(SentinelsNonTraites[0], SentinelsNonTraites, SR)
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


file = open("test_regroupement_sent", 'rb')
[Sent, Relations, seuil] = pickle.load(file)
file.close()
test1 = ClasseOnlySentinel(Sent[:1000], Relations, seuil)
test2 = ClasseOnlySentinelV2(Sent[:1000], Relations, seuil)

print(test1 == test2)
