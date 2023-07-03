import crontab as crontab
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pymongo
from bson import ObjectId
from DataPopulation import GeneratDocList
from AffiliatesTools import build_invites_chain ,BuildNetworkBalances, GenerateAffiliateCode
#from flask_crontab import Crontab
from TransactionsUtils import WithdrawBalance
from web3 import Web3
from web3.exceptions import ContractLogicError


app = Flask(__name__)
#app.secret_key = 'secret_key'
CORS(app)

# Configuration MongoDB
client = pymongo.MongoClient("mongodb+srv://Chris:qazwsx123@cluster0.gyca1sv.mongodb.net/?retryWrites=true&w=majority")

db = client.DAWGPT
users_collection = db.Users
Stacking_collection = db.Stacking
Info_collection=db.Info
Project_collection=db.Projects



for x in users_collection.find():
    print(x)

# Configuration flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


WALLET_KEY="0x865997f90bf55b694098cdb8e92bad3f9b035f54"

#crontab = Crontab(app)

#Available-Balance Refresh
@crontab.job(day="15")
@app.route('/RefreshBalances',)
def RefreshAvailableBalance():

    InterestRates=Info_collection.find_one({"Type":"Rendimenti"})
    NewAvailableBalnances={}

    for x in users_collection.find():

        #Calculate Returns on own invested resources
        NewPersonalBalance = (float(x["Current_balance"])/100)*InterestRates["RendimentoMensile_Investito"]

        # Calculate Returns on Network users invested resources
        Balance1, Balance2, Balance3, Balance4 = BuildNetworkBalances(x["AffiliateCode"], users_collection)

        ReturnLevel1 = (Balance1 / 100) * InterestRates["RendimentoMensile_Livello1"]
        ReturnLevel2 = (Balance2 / 100) * InterestRates["RendimentoMensile_Livello2"]
        ReturnLevel3 = (Balance3 / 100) * InterestRates["RendimentoMensile_Livello3"]
        ReturnLevel4 = (Balance4 / 100) * InterestRates["RendimentoMensile_Livello4"]

        TotalNetworkEarnings = round(ReturnLevel1 + ReturnLevel2 + ReturnLevel3 + ReturnLevel4, 2)


        #Calculate Total Earnings
        TotalEarnings=NewPersonalBalance+TotalNetworkEarnings
        NewAvailableBalnances[x["_id"]]=TotalEarnings


    for user_id, increment in NewAvailableBalnances.items():
        users_collection.update_one({'_id': user_id}, {'$inc': {'Current_balance': increment}})



# User Class for flask_login
class User(UserMixin):
    def __init__(self, username, password,AffiliateCode):
        self.id = username
        self.password = password
        self.AffiliateCode=AffiliateCode

# callback function for user research
@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'username': user_id})
    if not user:
        return None
    return User(user['username'], user['password'],user['AffiliateCode'])

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        InvitedBy=request.json["refferal"]

        AffiliatesCodeList = Info_collection.find_one({"Type": "AffiliateCodeList"})["AffiliateList"]

        print(AffiliatesCodeList)
        if users_collection.find_one({'username': username}):
            return jsonify({'message': 'Username già esistente'})
        if InvitedBy not in AffiliatesCodeList:
            return jsonify({'message': 'Codice Reffereal Non Valido!'})


        AffiliateCode = GenerateAffiliateCode()
        while AffiliateCode in AffiliatesCodeList:
            AffiliateCode = GenerateAffiliateCode()

        print(AffiliateCode)
        #update info aggiungendo a lista
        Info_collection.update_one({"Type":"AffiliateCodeList"}, {"$push": {"AffiliateList": AffiliateCode}})

        UserInfo={
            'username': username,
            'password': password,
            'Current_balance':0.0,
            'Available_Balance':0.0,
            'public_key':"",
            'transactions':[],
            'AffiliateCode':AffiliateCode,
            'InvitedBy':InvitedBy
        }



        response=users_collection.insert_one(UserInfo)
        return jsonify({'message': 'Registrazione effettuata'})
    return render_template('register.html')

# Access Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']

        user = users_collection.find_one({'username': username, 'password': password})


        if user is not None:
            user_obj = User(user['username'], user['password'],user["AffiliateCode"])
            login_user(user_obj)
            return redirect('/dashboard')
            #return jsonify({'message': 'Accesso consentito'})

        #return jsonify({'message': 'Credenziali non valide'})

    return render_template('login.html')

# Logout Page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Dashboard Area
@app.route('/dashboard')
@login_required
def dashboard():
    # Recupera l'oggetto User dell'utente autenticato
    user = current_user

    user_document = users_collection.find_one({'username': user.id})

    if user_document:
        # Recupera i valori desiderati dal documento utente
        current_balance = user_document.get('Current_balance')
        available_balance = user_document.get('Available_Balance')
        public_key = user_document.get('public_key')
        transactions_list = user_document.get('transactions', [])

        # Restituisci i valori come JSON
        return render_template('dashboard.html', Current_balance=current_balance, AvailableBalance=available_balance,
                               PublicKey=public_key, transactions_list=transactions_list)

    else:
        # Gestisci il caso in cui l'utente non esiste nel database
        return jsonify({'error': 'User not found'})


    # Renderizza la pagina dashboard con il Current_balance dell'utente

#Update Public key
@app.route('/update_public_key', methods=['POST'])
@login_required
def update_public_key():

    user = current_user
    user_id = user.id

    if 'public_key' in request.form:
        public_key = request.form['public_key']

        # Aggiorna la chiave pubblica dell'utente nel database
        users_collection.update_one({'username': user_id}, {'$set': {'public_key': public_key}})

        # Reindirizza alla pagina dashboard
        return redirect(url_for('dashboard'))
    else:
        # Gestisci il caso in cui la chiave pubblica non è stata fornita
        return jsonify({'error': 'Public key missing'})


#Reinvest Balance
@app.route('/Reinvest_balance', methods=['POST'])
@login_required
def Reinvest_balance():

    Balance_To_Reinvest = float(request.form['Reinvest_balance'])
    user_id = current_user.id
    Max_Reinvestable_Balance=float(users_collection.find_one({'username': user_id})['Available_Balance'])
    Current_balance = float(users_collection.find_one({'username': user_id})['Current_balance'])

    if Balance_To_Reinvest<=Max_Reinvestable_Balance:
        NewAvailableBalance=Max_Reinvestable_Balance-Balance_To_Reinvest
        NewSaldo=Current_balance+Balance_To_Reinvest
    else:
        return jsonify({'message': 'Ammount Non Valido'})


    users_collection.update_one({'username': user_id}, {'$set': {'Available_Balance': NewAvailableBalance,'Current_balance':NewSaldo}})


    return redirect(url_for('dashboard'))


#Whitdraw Crypto
@app.route('/WithdrawCrypto', methods=['POST'])
@login_required
def WithdrawCrypto():
    AmmountToWithdraw = request.form['Withdraw_balance']
    user_id = current_user.id
    AvailableBalance = users_collection.find_one({'username': user_id})['Available_Balance']
    recipient_address = users_collection.find_one({'username': user_id})['public_key']

    if float(AmmountToWithdraw)<=AvailableBalance:
        # Indirizzo del wallet mittente
        SENDER_ADDRESS = '0x0e680F62C46ea6F7EEAA1a01177674123b64BF6c'

        # Chiave privata del wallet mittente
        PRIVATE_KEY = '2ac338fa6a34fdb9d2aa561b072076ffa69316716c2523f7dfbff412507fa335'

        print("kkkkk")
        WithdrawBalance(recipient_address, AmmountToWithdraw,SENDER_ADDRESS,PRIVATE_KEY)
    else:
        print("Balance Insufficiente")

    return redirect(url_for('dashboard'))





#Stacking Area
@app.route('/Stacking')
@login_required
def Stacking():


    return render_template('Stacking.html',WalletKey=WALLET_KEY)





#Affiliates
@app.route('/Affiliates')
@login_required
def Affiliates():
    # Recupera l'oggetto User dell'utente autenticato
    user = current_user

    level1, level2, level3, level4 = build_invites_chain(current_user.AffiliateCode, users_collection)


    return render_template('Affiliates.html',Level1=level1,Level2=level2,Level3=level3,Level4=level4)

#Rewards
@app.route('/Rewards')
@login_required
def Rewards():
    # Recupera l'oggetto User dell'utente autenticato
    user = current_user

    InterestRates=Info_collection.find_one({"Type":"Rendimenti"})

    Balance1,Balance2,Balance3,Balance4=BuildNetworkBalances(current_user.AffiliateCode,users_collection)


    ReturnLevel1 = (Balance1/100) * InterestRates["RendimentoMensile_Livello1"]
    ReturnLevel2 = (Balance2/100) * InterestRates["RendimentoMensile_Livello2"]
    ReturnLevel3 = (Balance3/100) * InterestRates["RendimentoMensile_Livello3"]
    ReturnLevel4 = (Balance4/100) * InterestRates["RendimentoMensile_Livello4"]

    TotalNetworkEarnings=round(ReturnLevel1+ReturnLevel2+ReturnLevel3+ReturnLevel4,2)
    PersonalEarnings= round((float(users_collection.find_one({'username': user.id})['Current_balance'])/100)*InterestRates["RendimentoMensile_Investito"],2)


    return render_template('Rewards.html',Balance1=Balance1,Balance2=Balance2,Balance3=Balance3,Balance4=Balance4,TotalNetworkEarnings=TotalNetworkEarnings,PersonalEarnings=PersonalEarnings)






























































if __name__ == '__main__':
    app.run(debug=True)


