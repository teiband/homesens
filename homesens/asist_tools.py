from flask import Flask, render_template, request, Markup, Blueprint
from asist.tools import convert_all_prices_to_currency
import finnhub

convert_currency_page = Blueprint('convert_currency', __name__, template_folder='templates')

@convert_currency_page.route('/asist-tools')
def asist_tools_page():
    return render_template('asist_tools.html')

@convert_currency_page.route('/convert-currency', methods = ['POST', 'GET'])
def convert_currency():
    if request.method == 'GET':
        return render_template('convert_currency.html', response_data=[])
    if request.method == 'POST':
        form_data = request.form
        text = form_data['text']
        converted_text = convert_all_prices_to_currency(text)
        lines = text.split('\n')
        response_data = dict()
        response_data['original_text'] = text.split('\n')
        response_data['converted_text'] = converted_text.split('\n')
        return render_template('convert_currency.html', response_data=response_data )

@convert_currency_page.route('/symbol-lookup', methods = ['POST', 'GET'])
def symbol_lookup():
    if request.method == 'GET':
        return render_template('symbol_lookup.html', response_data=[])
    if request.method == 'POST':
        finnhub_client = finnhub.Client(api_key="c14lb8f48v6st2753nig")
        res = finnhub_client.symbol_lookup(request.form['symbol'])
        print(res)
        response_data = dict(symbol=res['result'])
        return render_template('symbol_lookup.html', response_data=response_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)