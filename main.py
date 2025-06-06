from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print("Received alert:", data)
    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
