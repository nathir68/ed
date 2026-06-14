from flask import Flask, render_template, request

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. Create the main route (Home Page)
@app.route('/')
def home():
    # This will look for a file called 'home.html' inside the 'templates' folder
    return render_template('home.html')

# 3. Create a route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get the data the user typed in the form
    user_name = request.form.get('username')
    
    # Return a simple greeting
    return f"<h1>Hello, {user_name}! You successfully wrote your first backend code.</h1>"

# 4. Start the server
if __name__ == '__main__':
    # debug=True means the server will auto-restart if you change the code
    app.run(debug=True, port=5001)
