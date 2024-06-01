from flask import Flask, request, jsonify, render_template


app = Flask(__name__)


@app.route('/')
def frontend():
    return render_template('index.html')




# Run the app
if __name__ == '__main__':
    app.run(debug=True)