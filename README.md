# 🧬 User Management System - Genetic Invent

Demo project connecting a frontend hosted on **GitHub Pages** with a **PHP** backend hosted on **Hostinger**.

## 🎯 Project Goal

This project is designed to teach Genetic Invent employees how to:
- Connect Frontend with Backend
- Use CRUD operations (Create, Read, Update, Delete)
- Communicate with APIs using JavaScript fetch()
- Understand MySQL database functionality

## 📁 Project Contents

### 1. `index.html` - Frontend
- Single HTML file containing CSS and JavaScript
- Hosted on **GitHub Pages**
- Provides interactive user interface for user management
- Contains explanatory tooltips for each element
- Displays API source code for educational purposes

### 2. `api.php` - Backend
- PHP file running on **Hostinger** server
- Handles MySQL database operations
- Provides API for CRUD operations
- Automatically creates users table on first use

## 🚀 Setup Instructions

### Step 1: Backend Already Deployed

The backend is already deployed and configured:
1. **Website**: http://glconnectionbuilder1.com/
2. **API Endpoint**: http://glconnectionbuilder1.com/api.php
3. **Database Configuration**:
   ```php
   const DB_HOST = 'localhost';
   const DB_NAME = 'u419999707_Demo';
   const DB_USER = 'u419999707_NaifDemo';
   const DB_PASS = 'P@master5007';
   ```

### Step 2: Update API URL

In `index.html` file, the API URL is already configured for:
```javascript
const API_URL = 'http://glconnectionbuilder1.com/api.php';
```
This points to your Hostinger website where the API is hosted.

### Step 2: Upload Frontend to GitHub Pages

1. Create a new repository on GitHub
2. Upload `index.html` file
3. Enable GitHub Pages from repository settings
4. Choose main branch as source for publishing

### Step 3: Test the Application

You can test the API directly by visiting these URLs in your browser:
- **API Info (HTTPS)**: https://glconnectionbuilder1.com/api.php
- **API Info (HTTP)**: http://glconnectionbuilder1.com/api.php  
- **Connection Test**: https://glconnectionbuilder1.com/api.php?action=test_connection
- **View Users**: https://glconnectionbuilder1.com/api.php?action=read
- **System Stats**: https://glconnectionbuilder1.com/api.php?action=stats

**If HTTPS doesn't work, try the HTTP versions of these URLs.**

## 🔧 Educational Features

### Interactive Tooltips
- Hover over any element in the interface to see explanation of its function
- Each tooltip explains the code or logic behind the element

### API Code Display
- "View API Code" button opens modal window showing source code
- Useful for employees to understand backend functionality

### Demo Data
- When server connection is unavailable, system displays demo data
- Employees can test the interface even if API is not working

## 📊 Available CRUD Operations

### 1. Create User (Create)
- Fill form with required data
- Validate data accuracy
- Send POST request to API

### 2. Read Users (Read)
- Display list of all users
- Automatic data refresh
- Send GET request to API

### 3. Update User (Update)
- Select "Edit" from table
- Modify data in form
- Send POST request with action=update

### 4. Delete User (Delete)
- Select "Delete" from table
- Confirm deletion
- Send POST request with action=delete

## 🗄️ Database Information

### Database Credentials (Demo)
- **Database Name**: u419999707_Demo
- **Username**: u419999707_NaifDemo
- **Website**: glconnectionbuilder1.com
- **Password**: P@master5007

### Database Structure

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🔒 Security

- Data validation at PHP level
- Use Prepared Statements to prevent SQL Injection
- Input data sanitization
- CORS settings to allow requests from GitHub Pages

## 🐛 Troubleshooting

### CORS Issues
If CORS errors appear, ensure these headers exist in `api.php`:
```php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
```

### Database Issues
- Verify connection data accuracy
- Check that database exists
- Review error logs in Hostinger

### JavaScript Issues
- Open developer tools in browser
- Check Console tab for errors
- Verify API URL accuracy

## 📚 Learn More

This project demonstrates the following concepts:
- **Frontend-Backend Communication**
- **RESTful API Design**
- **Database Operations**
- **Error Handling**
- **User Interface Design**
- **Security Best Practices**

## 📞 Support

For help or inquiries, refer to:
- Source code comments
- Interactive tooltips in interface
- Error logs in browser and Hostinger control panel

---

**This project was created for educational purposes for Genetic Invent Company** 🧬 