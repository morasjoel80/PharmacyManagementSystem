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

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Securepassword@0',
        database='pharmacy_management',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE customers
                SET User_ID = %s,
                    C_Name = %s,
                    C_Email = %s,
                    PhoneNumber = %s,
                    Address = %s
                WHERE Customer_ID = %s
            """
            cursor.execute(sql, (
                data['User_ID'],
                data['C_Name'],
                data['C_Email'],
                data['PhoneNumber'],
                data['Address'],
                id
            ))
            conn.commit()
        return jsonify({'message': 'Customer updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/employees')
def employees_page():
    return "<h2>Employees Module - Coming Soon</h2>"

@app.route('/orders')
def orders_page():
    return "<h2>Orders Module - Coming Soon</h2>"

@app.route('/payment_methods')
def payment_methods_page():
    return "<h2>Payment Methods - Coming Soon</h2>"

@app.route('/prescriptions')
def prescriptions_page():
    return "<h2>Prescriptions - Coming Soon</h2>"

@app.route('/suppliers')
def suppliers_page():
    return "<h2>Suppliers - Coming Soon</h2>"

@app.route('/users')
def users_page():
    return "<h2>Users Module - Coming Soon</h2>"


@app.route('/')
def index():
    return redirect('/login')

@app.route('/admin_home')
def admin_home():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin_home.html', user=session['user'])


@app.route('/staff_home')
def staff_home():
    if 'user' not in session or session.get('role') != 'employee':
        return redirect('/login')
    return render_template('staff_home.html', user=session['user'])


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
            # Query to get user details including role
            cursor.execute("SELECT * FROM users WHERE U_Email=%s AND Password=%s", (email, password))
            user = cursor.fetchone()
            print("LOGIN DEBUG:", user)

            if user:
                # Store user's name in session
                session['user'] = user['U_Name']
                session['role'] = user['Role']  # Store role for role-based access

                # Redirect based on user role
                if user['Role'] == 'admin':
                    return redirect('/admin_home')  # Admin-specific home page
                else:
                    return redirect('/staff_home')  # Staff-specific home page
            else:
                error = 'Invalid credentials'
    return render_template('login.html', error=error)



@app.route('/home')
def home():
    if 'role' in session:
        role = session['role']
        if role == 'admin':
            return render_template('admin_home.html', user=session['user'])
        else:
            return render_template('staff_home.html', user=session['user'])
    return redirect('/login')


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

@app.route('/medicines/<int:id>', methods=['PUT'])
def update_medicine(id):
    data = request.json

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Securepassword@0',
        database='pharmacy_management',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE medicines
                SET M_Name=%s, Price=%s, Quantity_in_stock=%s, Expiry_date=%s, Supplier_ID=%s, Category=%s
                WHERE Medicine_ID=%s
            """
            cursor.execute(sql, (
                data['M_Name'],
                data['Price'],
                data['Quantity_in_stock'],
                data['Expiry_date'],
                data['Supplier_ID'],
                data['Category'],
                id
            ))
            conn.commit()
        return jsonify({'message': 'Medicine updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/sales-page')
def sales_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('sales.html')

@app.route('/sales', methods=['GET'])
def get_sales():
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Sales")
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

@app.route('/sales/<int:id>', methods=['GET'])
def get_sale(id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Sales WHERE Sales_ID = %s", (id,))
            sale = cursor.fetchone()
            if sale:
                return jsonify(sale)
            else:
                return jsonify({"error": "Sale not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sales/<int:id>', methods=['PUT'])
def edit_sale(id):
    data = request.get_json()
    customer_id = data['Customer_ID']
    date = data['Date']
    total_amount = data['Total_amount']
    payment_method_id = data['Payment_Method_ID']

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Sales
                SET Customer_ID = %s, Date = %s, Total_amount = %s, Payment_Method_ID = %s
                WHERE Sales_ID = %s
            """, (customer_id, date, total_amount, payment_method_id, id))
            conn.commit()
        return jsonify({"message": "Sale updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory')
def inventory_page():
    return render_template('inventory.html')


@app.route('/inventory', methods=['POST'])
def add_inventory():
    try:
        data = request.get_json()
        medicine_id = data.get('Medicine_ID')
        stock_quantity = data.get('StockQuantity')
        reorder_level = data.get('Reorder_Level')

        if not all([medicine_id, stock_quantity, reorder_level]):
            return jsonify({"error": "Missing fields in request"}), 400

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Inventory (Medicine_ID, StockQuantity, Reorder_Level)
                VALUES (%s, %s, %s)
            """, (medicine_id, stock_quantity, reorder_level))
            conn.commit()

        return jsonify({"message": "Inventory added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/inventory', methods=['GET'])
def get_inventory():
    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    try:
        # Execute a query to get all inventory records from the 'inventory' table
        cursor.execute("SELECT * FROM inventory")

        # Fetch all rows from the result of the query
        inventory = cursor.fetchall()

        # Create a list to store the inventory data in the required format
        inventory_list = []
        for item in inventory:
            inventory_list.append({
                'Inventory_ID': item['Inventory_ID'],
                'Medicine_ID': item['Medicine_ID'],
                'StockQuantity': item['StockQuantity'],
                'Reorder_Level': item['Reorder_Level']
            })

        # Return the list of inventory items as a JSON response
        return jsonify(inventory_list)

    except Exception as e:
        # In case of an error, return a 500 error with the error message
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the cursor to release the database connection resources
        cursor.close()



@app.route('/inventory/<int:id>', methods=['PUT'])
def update_inventory(id):
    data = request.get_json()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE Inventory
            SET Medicine_ID = %s, StockQuantity = %s, Reorder_Level = %s
            WHERE Inventory_ID = %s
        """, (data['Medicine_ID'], data['StockQuantity'], data['Reorder_Level'], id))
        conn.commit()
    return jsonify({"message": "Inventory updated successfully"})

@app.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM Inventory WHERE Inventory_ID = %s", (id,))
        conn.commit()
    return jsonify({"message": "Inventory deleted successfully"})






if __name__ == '__main__':
    app.run(debug=True)