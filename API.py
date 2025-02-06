from flask import Flask, jsonify

@app.route("/", methods=['GET'])
def landing():
    pass

@app.route("/register", methods=['POST'])
def register(user):
    pass

@app.route("/profile", methods=['POST'])
def retrieve(meterid):
    pass

@app.route('/profile/<meterid>', methods=['GET'])
def userlanding(meterid):
    pass

@app.route('/profile/<meterid>/consumption', methods=['GET'])
def consumption(meterid):
    pass

@app.route('/profile/<meterid>/consumption', methods=['GET']) #add the ?period thing
def consumption(meterid):
    pass

@app.route('/profile/<meterid>/consumption/download', methods=['GET'])
def downloadconsumption():
    pass

@app.route('/meter', methods=['POST'])
def meterfeed():
    pass