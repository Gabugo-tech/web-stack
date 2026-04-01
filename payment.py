from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)
CORS(app)

# Set your Stripe secret key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_YOUR_STRIPE_SECRET_KEY')

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.get_json()
        amount = data['amount']
        currency = data.get('currency', 'ngn')
        description = data.get('description', 'Payment')

        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to kobo for NGN
            currency=currency,
            description=description,
            payment_method_types=['card'],
        )

        return jsonify({
            'clientSecret': payment_intent.client_secret,
            'id': payment_intent.id,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    try:
        data = request.get_json()
        payment_intent_id = data['paymentIntentId']
        payment_method_id = data['paymentMethodId']

        confirmed = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method={'id': payment_method_id}
        )

        return jsonify({'status': confirmed.status})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = 'whsec_YOUR_WEBHOOK_SECRET'  # Replace with your webhook secret

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        if event['type'] == 'payment_intent.succeeded':
            print('Payment successful:', event['data']['object'])

        return jsonify({'received': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3000)