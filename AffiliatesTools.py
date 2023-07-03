import random
import string
from datetime import datetime

def build_invites_chain(invited_by,users_collection):
    level1 = []
    level2 = []
    level3 = []
    level4 = []

    # ricerca degli utenti invitati dal diretto inviatore
    for user in users_collection.find({'InvitedBy': invited_by}):
        level1.append(user)

    # ricerca degli utenti invitati dal livello 1
    for user2 in level1:
        for x in users_collection.find({'InvitedBy': user2['AffiliateCode']}):
            if x not in level2:
                level2.append(x)

    # ricerca degli utenti invitati dal livello 2
    for user3 in level2:
        for y in users_collection.find({'InvitedBy': user3['AffiliateCode']}):
            if y not in level3:
                level3.append(y)

    # ricerca degli utenti invitati dal livello 3
    for user4 in level3:
        for w in users_collection.find({'InvitedBy': user4['AffiliateCode']}):
            if w not in level4:
                level4.append(w)

        # interrompe il ciclo se level4 è vuota
        if not level4:
            break

    return level1, level2, level3, level4

def BuildNetworkBalances(invited_by,users_collection):
    level1 = []
    level2 = []
    level3 = []
    level4 = []


    level1Balance = 0.0
    level2Balance = 0.0
    level3Balance = 0.0
    level4Balance = 0.0

    # ricerca degli utenti invitati dal diretto inviatore
    for user in users_collection.find({'InvitedBy': invited_by}):
        level1.append(user)
        level1Balance= level1Balance+user["Current_balance"]

    # ricerca degli utenti invitati dal livello 1
    for user2 in level1:
        for x in users_collection.find({'InvitedBy': user2['AffiliateCode']}):
            if x not in level2:
                level2.append(x)
                level2Balance = level2Balance+ x["Current_balance"]

    # ricerca degli utenti invitati dal livello 2
    for user3 in level2:
        for y in users_collection.find({'InvitedBy': user3['AffiliateCode']}):
            if y not in level3:
                level3.append(y)
                level3Balance = level3Balance+ y["Current_balance"]

    # ricerca degli utenti invitati dal livello 3
    for user4 in level3:
        for w in users_collection.find({'InvitedBy': user4['AffiliateCode']}):
            if w not in level4:
                level4.append(w)
                level4Balance = level4Balance+ w["Current_balance"]

        # interrompe il ciclo se level4 è vuota
        if not level4:
            break

    return round(level1Balance,2), round(level2Balance,2), round(level3Balance,2), round(level4Balance,2)

def GenerateAffiliateCode():
    caratteri = string.ascii_letters + string.digits
    return ''.join(random.choice(caratteri) for _ in range(10))




