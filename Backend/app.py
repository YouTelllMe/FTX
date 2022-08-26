from numpy import true_divide
from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS, cross_origin
import client_api_new as client_api
import json 

app = Flask(__name__)



CORS(app)


@app.route('/API',methods=['POST'])
@cross_origin()
def API():
    param = request.get_json()
    type = param['type']
    with open("api_config.txt", "r") as config:
        account = json.loads(config.read())
        client = client_api.FtxClient(account['api_key'],account['api_secret'], account['subaccount'])
    if type == 'graph_rates':
        return jsonify(client.graph_rates(param['coin']))
    elif type == 'get_coins':
        return jsonify(client.coins)
    elif type == 'graph_payments':
        return jsonify(client.graph_payments(param['coin']))
    elif type == 'payments-list':
        return jsonify(client.payment_list())
    elif type == 'graph_borrow':
        return jsonify(client.borrow_history(param['coin']))
    elif type == 'graph_all':
        return jsonify(client.get_total())
    elif type == 'read_client_orders':
        with open('orders.txt','r') as orders:
            return jsonify(orders.read())
    elif type == 'post_client_orders':
        data = param['data']
        with open('orders.txt','w') as orders:
            orders.write(json.dumps(data))
        return jsonify("success")
    elif type == 'get_balance':
        return jsonify(client.get_account_info())
    elif type == 'get_config':
        return jsonify(client.get_config())
    elif type == 'post_config':
        data = param['data']
        if client_api.FtxClient(data['api_key'],data['api_secret'], data['subaccount']).get_account_info() == False:
            return jsonify("failure")
        else: 
            with open("api_config.txt", "w") as config:
                config.write(json.dumps(data))
            return jsonify("success")
    elif type == 'get_subaccounts':
        return jsonify(client._get("subaccounts"))
    else:
        return jsonify({'status':'failure'})


@app.route('/API/tabledata')
def tabledata():
    with open("api_config.txt", "r") as config:
        account = json.loads(config.read())
        client = client_api.FtxClient(account['api_key'],account['api_secret'], account['subaccount'])
    return jsonify(client.table_data())

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/rates')
def rates():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('index.html')

@app.route('/order')
def order():
    return render_template('index.html')

@app.route('/settings')
def settings():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()