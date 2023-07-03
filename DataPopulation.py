import random
import string
from datetime import datetime

def generate_random_transactions(num_transactions):
    transactions = []
    for i in range(num_transactions):
        data = datetime.now().strftime('%d-%m-%Y')
        amount = round(random.uniform(100, 1000), 2)
        transaction_hash = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        status = random.choice(['Done!', 'Pending', 'Failed'])
        transaction = {'Data': data, 'Amount': amount, 'TransactionHash': transaction_hash, 'Status': status}
        transactions.append(transaction)
    return transactions

def generate_random_doc():
    UserName=["BigJhon","Newbbie","Thorn","Gummy","INoob","crypto"]
    username = ""+random.choice(UserName) + str(random.randint(1, 100)) + "@gmail.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    saldo = round(random.uniform(1000, 5000), 2)
    available_balance = round(random.uniform(50, 500), 2)
    public_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
    transactions = generate_random_transactions(random.randint(1, 5))
    AffiliateCode=genera_AffiliateCode()
    doc = {'username': username, 'password': password,'AffiliateCode':AffiliateCode, 'saldo': saldo,'InvitedBy':'UiFlItVU', 'Available_Balance': available_balance, 'public_key': public_key, 'transactions': transactions}
    return doc


def genera_AffiliateCode():
    caratteri = string.ascii_letters + string.digits
    return ''.join(random.choice(caratteri) for _ in range(8))



def GeneratDocList(num_docs):
    DocList=[]
    for i in range(num_docs):
        doc = generate_random_doc()
        DocList.append(doc)
    return DocList