import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QStackedWidget, QTableWidget, QTableWidgetItem,
                           QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
import requests
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

class APIClient:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.base_url = 'http://localhost:8080'
        self.debug = True  # Enable debug mode for better error messages
    
    def set_token(self, token):
        self.token = token
        self.session.headers.update({'Authorization': f'Token {token}'})
    
    def make_request(self, method, endpoint, **kwargs):
        """Generic request method with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if self.debug:
                print(f"Making {method} request to: {url}")
            
            response = self.session.request(method, url, **kwargs)
            
            if self.debug:
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
            
            if response.status_code == 404:
                return False, "Server endpoint not found. Make sure the Django server is running."
            elif response.status_code == 500:
                return False, "Internal server error. Check Django server logs."
            elif response.status_code == 403:
                return False, "Permission denied. Check authentication."
            
            try:
                return True, response.json()
            except ValueError:
                return True, response.text
                
        except requests.exceptions.ConnectionError:
            return False, "Could not connect to server. Make sure Django is running on port 8080."
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"
    
    def login(self, username, password):
        """Login and get authentication token"""
        success, result = self.make_request(
            'POST',
            '/api/token/',
            json={'username': username, 'password': password}
        )
        
        if success and isinstance(result, dict) and 'token' in result:
            self.set_token(result['token'])
            return True, None
        return False, result or "Login failed"

    def get_analytics(self):
        """Get analytics data"""
        success, result = self.make_request('GET', '/api/dashboard/analytics/')
        return result if success else None
    
    def get_requests(self):
        """Get customer requests"""
        success, result = self.make_request('GET', '/api/dashboard/requests/')
        return result if success else None
    
    def get_sales_analytics(self, days=30):
        """Get sales analytics data"""
        success, result = self.make_request(
            'GET',
            '/api/dashboard/sales/',
            params={'days': days}
        )
        return result if success else None
    
    def upload_update(self, file_path, data):
        """Upload a file update"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                success, result = self.make_request(
                    'POST',
                    '/api/dashboard/updates/',
                    data=data,
                    files=files
                )
                return success, result
        except IOError as e:
            return False, f"File error: {str(e)}"

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metra Admin Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.api_client = APIClient()
        self.setup_ui()

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar.setMaximumWidth(200)

        # Sidebar buttons
        buttons = [
            ("Overview", self.show_overview),
            ("Upload Updates", self.show_upload_panel),
            ("Customer Requests", self.show_requests),
            ("Product Analytics", self.show_analytics),
            ("Settings", self.show_settings),
            ("Logout", self.logout)
        ]

        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Create stacked widget for main content
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Create pages
        self.create_login_page()
        self.create_overview_page()
        self.create_upload_page()
        self.create_requests_page()
        self.create_analytics_page()
        self.create_settings_page()

        # Show login page by default
        self.content_stack.setCurrentIndex(0)

    def create_login_page(self):
        login_page = QWidget()
        layout = QVBoxLayout(login_page)
        layout.setAlignment(Qt.AlignCenter)

        # Header
        header = QLabel("Metra Admin Dashboard")
        header.setFont(QFont('Arial', 24, QFont.Bold))
        layout.addWidget(header, alignment=Qt.AlignCenter)

        # Login form
        form = QWidget()
        form_layout = QVBoxLayout(form)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        form_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        form_layout.addWidget(login_button)

        layout.addWidget(form)
        self.content_stack.addWidget(login_page)

    def create_overview_page(self):
        overview_page = QWidget()
        layout = QVBoxLayout(overview_page)

        # Header
        header = QLabel("Dashboard Overview")
        header.setFont(QFont('Arial', 20, QFont.Bold))
        layout.addWidget(header)

        # Stats cards
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)

        stats = [
            ("Total Sales", "$15,234"),
            ("Active Users", "1,234"),
            ("New Orders", "56"),
            ("Pending Requests", "23")
        ]

        self.stats_values = {}
        for title, value in stats:
            card = QWidget()
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(title))
            value_label = QLabel(value)
            value_label.setFont(QFont('Arial', 16, QFont.Bold))
            card_layout.addWidget(value_label)
            stats_layout.addWidget(card)
            self.stats_values[title] = value_label

        layout.addWidget(stats_widget)

        # Charts
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)

        # Sales chart
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        dates = [datetime.now() - timedelta(days=x) for x in range(7)]
        values = [100, 120, 95, 134, 156, 145, 162]
        ax1.plot(dates, values)
        ax1.set_title('Weekly Sales')
        canvas1 = FigureCanvas(fig1)
        charts_layout.addWidget(canvas1)

        # Products chart
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones']
        values = [45, 32, 28, 21, 18]
        ax2.bar(products, values)
        ax2.set_title('Top Selling Products')
        plt.xticks(rotation=45)
        canvas2 = FigureCanvas(fig2)
        charts_layout.addWidget(canvas2)

        layout.addWidget(charts_widget)
        self.content_stack.addWidget(overview_page)

    def create_upload_page(self):
        upload_page = QWidget()
        layout = QVBoxLayout(upload_page)

        header = QLabel("Upload Updates")
        header.setFont(QFont('Arial', 20, QFont.Bold))
        layout.addWidget(header)

        # File selection
        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)

        choose_button = QPushButton("Choose File")
        choose_button.clicked.connect(self.choose_file)
        file_layout.addWidget(choose_button)

        layout.addWidget(file_widget)

        # Upload button
        upload_button = QPushButton("Upload")
        upload_button.clicked.connect(self.upload_file)
        layout.addWidget(upload_button)

        layout.addStretch()
        self.content_stack.addWidget(upload_page)

    def create_requests_page(self):
        requests_page = QWidget()
        layout = QVBoxLayout(requests_page)

        header = QLabel("Customer Requests")
        header.setFont(QFont('Arial', 20, QFont.Bold))
        layout.addWidget(header)

        # Requests table
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID', 'Customer', 'Type', 'Status', 'Date'])

        # Sample data
        sample_data = [
            ('1', 'John Doe', 'Support', 'Pending', '2024-03-03'),
            ('2', 'Jane Smith', 'Return', 'Processing', '2024-03-02'),
            ('3', 'Bob Johnson', 'Inquiry', 'Completed', '2024-03-01')
        ]

        table.setRowCount(len(sample_data))
        for i, row in enumerate(sample_data):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(value))

        layout.addWidget(table)
        self.content_stack.addWidget(requests_page)

    def create_analytics_page(self):
        analytics_page = QWidget()
        layout = QVBoxLayout(analytics_page)

        header = QLabel("Product Analytics")
        header.setFont(QFont('Arial', 20, QFont.Bold))
        layout.addWidget(header)

        # Add analytics charts
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)

        # Sales trend
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        dates = [datetime.now() - timedelta(days=x) for x in range(30)]
        values = np.random.normal(1000, 100, 30)
        ax1.plot(dates, values)
        ax1.set_title('30-Day Sales Trend')
        plt.xticks(rotation=45)
        canvas1 = FigureCanvas(fig1)
        charts_layout.addWidget(canvas1)

        # Category distribution
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        categories = ['Electronics', 'Accessories', 'Software', 'Services']
        sales = [4500, 2300, 1800, 1200]
        ax2.pie(sales, labels=categories, autopct='%1.1f%%')
        ax2.set_title('Sales by Category')
        canvas2 = FigureCanvas(fig2)
        charts_layout.addWidget(canvas2)

        layout.addWidget(charts_widget)
        self.content_stack.addWidget(analytics_page)

    def create_settings_page(self):
        settings_page = QWidget()
        layout = QVBoxLayout(settings_page)

        header = QLabel("Settings")
        header.setFont(QFont('Arial', 20, QFont.Bold))
        layout.addWidget(header)

        # Add settings controls here
        layout.addStretch()
        self.content_stack.addWidget(settings_page)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password!")
            return

        success, error = self.api_client.login(username, password)
        if success:
            self.show_overview()
            self.update_dashboard_data()
        else:
            QMessageBox.warning(self, "Login Failed", error or "Failed to connect to server")

    def update_dashboard_data(self):
        # Update overview data
        sales_data = self.api_client.get_sales_analytics()
        if sales_data:
            self.update_overview_stats(sales_data)
        
        # Update requests data
        requests_data = self.api_client.get_requests()
        if requests_data:
            self.update_requests_table(requests_data)
        
        # Update analytics data
        analytics_data = self.api_client.get_analytics()
        if analytics_data:
            self.update_analytics_charts(analytics_data)

    def update_overview_stats(self, data):
        if not hasattr(self, 'stats_values'):
            return
        
        self.stats_values['Total Sales'].setText(f"${data['total_sales']}")
        self.stats_values['Orders'].setText(str(data['orders_count']))
        self.stats_values['Avg Order'].setText(f"${data['average_order_value']}")
        
        # Update charts
        self.update_sales_chart(data.get('sales_by_day', []))
        self.update_products_chart(data.get('top_products', []))

    def update_requests_table(self, requests):
        table = self.findChild(QTableWidget)
        if not table:
            return
        
        table.setRowCount(len(requests))
        for i, req in enumerate(requests):
            table.setItem(i, 0, QTableWidgetItem(str(req['id'])))
            table.setItem(i, 1, QTableWidgetItem(req['username']))
            table.setItem(i, 2, QTableWidgetItem(req['request_type']))
            table.setItem(i, 3, QTableWidgetItem(req['status']))
            table.setItem(i, 4, QTableWidgetItem(req['created_at']))

    def upload_file(self):
        if self.file_label.text() == "No file selected":
            QMessageBox.warning(self, "Error", "Please select a file first!")
            return
        
        data = {
            'title': 'Update ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'update_type': 'system',
            'description': 'System update uploaded via admin dashboard',
            'version': '1.0.0'
        }
        
        success, result = self.api_client.upload_update(self.file_label.text(), data)
        if success:
            QMessageBox.information(self, "Success", "File uploaded successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Upload failed: {result}")

    def show_overview(self):
        if self.api_client.token:
            self.content_stack.setCurrentIndex(1)

    def show_upload_panel(self):
        if self.api_client.token:
            self.content_stack.setCurrentIndex(2)

    def show_requests(self):
        if self.api_client.token:
            self.content_stack.setCurrentIndex(3)

    def show_analytics(self):
        if self.api_client.token:
            self.content_stack.setCurrentIndex(4)

    def show_settings(self):
        if self.api_client.token:
            self.content_stack.setCurrentIndex(5)

    def logout(self):
        self.api_client.token = None
        self.api_client.session.headers.pop('Authorization', None)
        self.content_stack.setCurrentIndex(0)
        self.username_input.clear()
        self.password_input.clear()

    def choose_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filename:
            self.file_label.setText(filename)

def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()