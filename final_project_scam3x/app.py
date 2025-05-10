from flask import Flask, render_template, request, url_for, redirect
import mysql.connector
from mysql.connector import errorcode
import pygal
from pygal import Config
from pygal.style import *
import sys

#create a flask app object and set app variables
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'your secret key'
app.secret_key = 'your secret key'

#create a connection object to the module2 database
def get_db_connection():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            port="6603",
            database="classicmodels"
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password.")
            exit()
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
            exit()
        else:
            print(err)
            print("ERROR: Service not available")
            exit()

    return mydb
    

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        section = request.form.get('section')
        if section:
            return redirect(url_for(section))
    return render_template('index.html')

@app.route('/product-reports', methods = ['GET', 'POST'])
def products_reports():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary = True)

    cursor.execute("SELECT DISTINCT YEAR(orderDate) as year FROM orders ORDER BY year")
    years = [str(r['year']) for r in cursor.fetchall()]
    
    selected_year = request.args.get('year')
    report = request.args.get('report')
    rows = []
    chart = None

    raw_year = request.form.get('year')
    selected_year = selected_year if selected_year != "" else None
    
    # Convert selected_year to integer if it exists
    if selected_year:
        try:
            selected_year = int(selected_year)
        except ValueError:
            selected_year = None

    if report:
        
        try:
            config = Config()
            config.width = 800
            config.height = 200
            config.explicit_size = True

            compact_style = Style(
                label_font_size=8,
                major_label_font_size=10,
                title_font_size=8,
                legend_font_size=5,
                value_font_size=5,
                value_label_font_size=6,
                tooltip_font_size=8,
                no_data_font_size=6,
            )

            if report == "monthlyOrderTotals":
                query = """
                    SELECT year, month, totalSales
                    FROM monthlyOrderTotals
                    WHERE (%s IS NULL OR year = %s)
                    ORDER BY year, month
                """
                cursor.execute(query, (selected_year, selected_year))
                rows = cursor.fetchall()
                
                # Create bar chart
                bar_chart = pygal.Bar(style = compact_style, config = config)

                bar_chart.title = f'Monthly Order Totals for {selected_year if selected_year else "All Years"}'
                
                for row in rows:
                    bar_chart.add(f"{row['year']}-{row['month']}", row['totalSales'])
                
                chart = bar_chart.render_data_uri()

            elif report == "orderLineTotals":
                query = """
                    SELECT year, productLine, totalSales
                    FROM orderLineTotals
                    WHERE (%s IS NULL OR year = %s)
                    ORDER BY year, productLine
                """
                cursor.execute(query, (selected_year, selected_year))
                rows = cursor.fetchall()
                
                # Create line chart
                line_chart = pygal.Line(style = compact_style, config = config)
                line_chart.title = f'Order Line Totals for {selected_year if selected_year else "All Years"}'
                
                product_lines = list(set(row['productLine'] for row in rows))
                for product_line in product_lines:
                    data = [row['totalSales'] for row in rows if row['productLine'] == product_line]
                    line_chart.add(product_line, data)
                
                chart = line_chart.render_data_uri()

            elif report == "productOrderTotals":
                query = """
                    SELECT year, productName, totalSales
                    FROM productOrderTotals
                    WHERE (%s IS NULL OR year = %s)
                    ORDER BY totalSales DESC
                    LIMIT 10
                """
                cursor.execute(query, (selected_year, selected_year))
                rows = cursor.fetchall()
                
                # Create pie chart
                pie_chart = pygal.Pie(style = compact_style, config = config)
                pie_chart.title = f'Top 10 Products by Sales for {selected_year if selected_year else "All Years"}'
                
                for row in rows:
                    pie_chart.add(row['productName'], row['totalSales'])
                
                chart = pie_chart.render_data_uri()

        except Exception as e:
            print(f"Error fetching products: {e}", file=sys.stderr)
            rows = []
            chart = None

    cursor.close()
    mydb.close()

    return render_template('products.html', 
                         years=years,
                         rows=rows,
                         chart=chart,
                         selected_year=selected_year,
                         report=report)

@app.route('/customers-reports', methods=['GET', 'POST'])
def customers_reports():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Get all available years
    cursor.execute("SELECT DISTINCT YEAR(orderDate) as year FROM orders ORDER BY year")
    years = [str(r['year']) for r in cursor.fetchall()]
    
    selected_year = request.args.get('year')
    report = request.args.get('report')
    rows = []
    chart = None

    raw_year = request.form.get('year')
    selected_year = selected_year if selected_year != "" else None
    
    # Convert selected_year to integer if it exists
    if selected_year:
        try:
            selected_year = int(selected_year)
        except ValueError:
            selected_year = None

    if report:
        try:
            config = Config()
            config.width = 800
            config.height = 200
            config.explicit_size = True

            compact_style = Style(
                label_font_size=8,
                major_label_font_size=10,
                title_font_size=8,
                legend_font_size=5,
                value_font_size=5,
                value_label_font_size=6,
                tooltip_font_size=8,
                no_data_font_size=6,
            )
            if report == "customerOrderTotals":
                query = """
                    SELECT year, customerName, totalOrders
                    FROM customerOrderTotals
                    WHERE (%s IS NULL OR year = %s)
                    ORDER BY totalOrders DESC
                    LIMIT 10
                """
                cursor.execute(query, (selected_year, selected_year))
                rows = cursor.fetchall()
                
                # Create horizontal bar chart
                bar_chart = pygal.HorizontalBar(style = compact_style, config = config)
                bar_chart.title = f'Top 10 Customers by Order Total for {selected_year if selected_year else "All Years"}'
                
                for row in rows:
                    bar_chart.add(row['customerName'], row['totalOrders'])
                
                chart = bar_chart.render_data_uri()

            elif report == "customerPaymentTotals":
                query = """
                    SELECT year, customerName, totalPayments
                    FROM customerPaymentTotals
                    WHERE (%s IS NULL OR year = %s)
                    ORDER BY totalPayments DESC
                    LIMIT 10
                """
                cursor.execute(query, (selected_year, selected_year))
                rows = cursor.fetchall()
                
                # Create funnel chart
                funnel_chart = pygal.Funnel(style = compact_style, config = config)
                funnel_chart.title = f'Top 10 Customers by Payment Total for {selected_year if selected_year else "All Years"}'
                
                for row in rows:
                    funnel_chart.add(row['customerName'], row['totalPayments'])
                
                chart = funnel_chart.render_data_uri()

        except Exception as e:
            print(f"Error fetching customers: {e}", file=sys.stderr)
            rows = []
            chart = None

    cursor.close()
    mydb.close()

    return render_template('customers.html',
                         years=years,
                         rows=rows,
                         chart=chart,
                         selected_year=selected_year,
                         report=report)

@app.route('/employees-reports', methods=['GET', 'POST'])
def employees_reports():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    # Get all available years
    cursor.execute("SELECT DISTINCT YEAR(orderDate) as year FROM orders ORDER BY year")
    years = [str(r['year']) for r in cursor.fetchall()]
    
    selected_year = request.args.get('year')
    report = request.args.get('report')
    rows = []
    chart = None

    raw_year = request.form.get('year')
    selected_year = selected_year if selected_year != "" else None
    
    # Convert selected_year to integer if it exists
    if selected_year:
        try:
            selected_year = int(selected_year)
        except ValueError:
            selected_year = None

    if report:
        try:
            config = Config()
            config.width = 1000
            config.height = 400
            config.explicit_size = True

            compact_style = Style(
                label_font_size=5,
                major_label_font_size=5,
                title_font_size=8,
                legend_font_size=4,
                value_font_size=4,
                value_label_font_size=5,
                tooltip_font_size=5,
                no_data_font_size=6,
            )
            if report == "employeeOrderTotals":
                query = """
                    SELECT YEAR(o.orderDate) AS year,
                           CONCAT(e.firstName, ' ', e.lastName) AS fullName,
                           COALESCE(SUM(od.quantityOrdered * od.priceEach), 0) AS totalOrders
                    FROM employees e
                    LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
                    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
                    LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber
                    WHERE (%s IS NULL OR YEAR(o.orderDate) = %s)
                    GROUP BY YEAR(o.orderDate), e.employeeNumber, e.firstName, e.lastName
                    ORDER BY totalOrders DESC
                """
                cursor.execute(query, (selected_year, selected_year))
                rows = cursor.fetchall()
                
                # Create radar chart
                radar_chart = pygal.Radar(style = compact_style, config = config)
                radar_chart.title = f'Employee Order Totals for {selected_year if selected_year else "All Years"}'
                
                for row in rows:
                    radar_chart.add(row['fullName'], row['totalOrders'])
                
                chart = radar_chart.render_data_uri()

            elif report == "employeeOrderNumbers":
                query = """
                    SELECT YEAR(o.orderDate) AS year,
                           CONCAT(e.firstName, ' ', e.lastName) AS fullName,
                           COUNT(DISTINCT o.orderNumber) AS numOrders
                    FROM employees e
                    LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
                    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
                    WHERE (%s IS NULL OR YEAR(o.orderDate) = %s)
                    GROUP BY YEAR(o.orderDate), e.employeeNumber, e.firstName, e.lastName
                    ORDER BY numOrders DESC
                """
                cursor.execute(query, (selected_year, selected_year))
                rows = cursor.fetchall()
                
                # Create dot chart
                dot_chart = pygal.Dot(style = compact_style, config = config)
                dot_chart.title = f'Employee Order Numbers for {selected_year if selected_year else "All Years"}'
                
                for row in rows:
                    dot_chart.add(row['fullName'], row['numOrders'])
                
                chart = dot_chart.render_data_uri()

        except Exception as e:
            print(f"Error fetching employees: {e}", file=sys.stderr)
            rows = []
            chart = None

    cursor.close()
    mydb.close()

    return render_template('employees.html',
                         years=years,
                         rows=rows,
                         chart=chart,
                         selected_year=selected_year,
                         report=report)

if __name__ == '__main__':
    app.run(port=5008, debug=True)