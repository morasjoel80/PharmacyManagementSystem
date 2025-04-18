from flask import Flask, render_template, request, redirect, session, url_for
import pymysql
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Securepassword@0',
    database='pharmacy_management',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/customers-page')
def customers_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('customers.html')

@app.route('/customers', methods=['GET'])
def get_customers():
    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    try:
        # Execute a query to get all customers from the 'customers' table
        cursor.execute("SELECT * FROM customers")

        # Fetch all rows from the result of the query
        customers = cursor.fetchall()

        # Create a list to store the customer data in the required format
        customer_list = []
        for customer in customers:
            customer_list.append({
                'Customer_ID': customer['Customer_ID'],  # Ensure the column names match the table structure
                'User_ID': customer['User_ID'],
                'C_Name': customer['C_Name'],
                'C_Email': customer['C_Email'],
                'PhoneNumber': customer['PhoneNumber'],
                'Address': customer['Address']
            })

        # Return the list of customers as a JSON response
        return jsonify(customer_list)

    except Exception as e:
        # In case of an error, return a 500 error with the error message
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor to release the database connection resources
        cursor.close()


@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        data = request.get_json()

        # Ensure data is being received correctly
        print("Received data:", data)

        cursor = conn.cursor()

        # Make sure you're inserting all necessary fields, including User_ID
        cursor.execute("""
            INSERT INTO customers (User_ID, C_name, C_email, PhoneNumber, Address)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['User_ID'], data['C_name'], data['C_email'], data['PhoneNumber'], data['Address']))

        conn.commit()

        # Confirm insertion was successful
        print(f"Customer added: {data['User_ID']} - {data['C_name']}")

        return jsonify({'message': 'Customer added successfully'}), 201

    except Exception as e:
        print("Error while adding customer:", e)
        return jsonify({'error': 'An error occurred while adding customer'}), 500

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE Customer_ID = %s", (id,))
    conn.commit()
    return jsonify({'message': 'Customer deleted successfully'})
@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            error = 'Please enter both email and password'
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE U_email=%s AND Password=%s", (email, password))
            user = cursor.fetchone()
            print("LOGIN DEBUG:", user)

            if user and 'U_Name' in user:
                session['user'] = user['U_Name']
                return redirect('/home')
            else:
                error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('home.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/medicines-page')
def medicines_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('medicines.html')


@app.route('/medicines', methods=['GET'])
def get_medicines():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicine")
    medicines = cursor.fetchall()
    return jsonify(medicines)


@app.route('/medicines', methods=['POST'])
def add_medicine():
    data = request.get_json()

    # Extract and validate fields
    m_name = data.get('M_Name')
    price = data.get('Price')
    quantity = data.get('Quantity_in_stock')
    expiry = data.get('Expiry_date')
    supplier_id = data.get('Supplier_ID')
    category = data.get('Category')

    # Ensure required fields are present (optional, since schema allows NULL)
    if not all([m_name, price, quantity, expiry, supplier_id, category]):
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicine (M_Name, Price, Quantity_in_stock, Expiry_date, Supplier_ID, Category)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (m_name, price, quantity, expiry, supplier_id, category))
    conn.commit()
    return jsonify({'message': 'Medicine added successfully'})
@app.route('/medicines/<int:id>', methods=['DELETE'])
def delete_medicine(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE Medicine_ID = %s", (id,))
    conn.commit()
    return jsonify({'message': 'Medicine deleted successfully'})

@app.route('/sales-page')
def sales_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('sales.html')

@app.route('/sales', methods=['GET'])
def get_sales():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sales
    """)
    sales = cursor.fetchall()
    return jsonify(sales)

@app.route('/sales', methods=['POST'])
def add_sale():
    data = request.get_json()
    customer_id = data.get('Customer_ID')
    date = data.get('Date')
    total_amount = data.get('Total_amount')
    payment_method_id = data.get('Payment_Method_ID')

    if not all([customer_id, date, total_amount, payment_method_id]):
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales (Customer_ID, Date, Total_amount, Payment_Method_ID)
        VALUES (%s, %s, %s, %s)
    """, (customer_id, date, total_amount, payment_method_id))
    conn.commit()
    return jsonify({'message': 'Sale recorded successfully'})

@app.route('/sales/<int:id>', methods=['DELETE'])
def delete_sale(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales WHERE Sales_ID = %s", (id,))
    conn.commit()
    return jsonify({'message': 'Sale deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)