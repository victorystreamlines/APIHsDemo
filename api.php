<?php
/**
 * User Management System - API Backend
 * Demo project for Genetic Invent Company
 * 
 * This file provides API for handling CRUD operations on users
 * Runs on Hostinger server with MySQL database
 */

// Database configuration - Hostinger
const DB_HOST = 'localhost';
const DB_NAME = 'u419999707_Demo';
const DB_USER = 'u419999707_NaifDemo';
const DB_PASS = 'P@master5007';
const DB_PORT = 3306;

// Enable error reporting for development (should be disabled in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// CORS settings to allow requests from any origin (for demo purposes)
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, Origin');
header('Access-Control-Allow-Credentials: false');
header('Content-Type: application/json; charset=utf-8');

// Additional headers for better compatibility
header('Vary: Origin');
header('Cache-Control: no-cache, must-revalidate');

// Handle OPTIONS requests (preflight requests)
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    http_response_code(200);
    exit();
}

/**
 * Function to log errors and operations
 */
function logMessage($message, $type = 'INFO') {
    $timestamp = date('Y-m-d H:i:s');
    $logEntry = "[$timestamp] [$type] $message" . PHP_EOL;
    
    // Can save logs to file if needed
    // file_put_contents('api_log.txt', $logEntry, FILE_APPEND);
    
    // For development: display in console
    if ($type == 'ERROR') {
        error_log($logEntry);
    }
}

/**
 * Function to validate email
 */
function validateEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

/**
 * Function to validate phone number
 */
function validatePhone($phone) {
    // Simple pattern for phone number validation
    return preg_match('/^[0-9+\-\s()]{10,20}$/', $phone);
}

/**
 * Function to send JSON response
 */
function sendResponse($success, $message, $data = null, $httpCode = 200) {
    http_response_code($httpCode);
    
    $response = [
        'success' => $success,
        'message' => $message,
        'timestamp' => date('Y-m-d H:i:s')
    ];
    
    if ($data !== null) {
        $response['data'] = $data;
    }
    
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit();
}

try {
    // Log request start
    logMessage("API Request: " . $_SERVER['REQUEST_METHOD'] . " " . $_SERVER['REQUEST_URI']);
    
    // Database connection with better error handling
    $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";port=" . DB_PORT . ";charset=utf8mb4";
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
    ];
    
    $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
    logMessage("Database connection established successfully");
    
    // Test the connection
    $pdo->query("SELECT 1");
    logMessage("Database test query successful");

    // Create users table if it doesn't exist
    $createTableQuery = "
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ";
    
    $pdo->exec($createTableQuery);
    logMessage("Users table checked/created successfully");

    // Determine required action
    $action = $_POST['action'] ?? $_GET['action'] ?? '';
    logMessage("Action requested: " . $action);

    switch ($action) {
        case 'create':
            // === Create new user ===
            logMessage("Processing CREATE user request");
            
            $name = trim($_POST['name'] ?? '');
            $email = trim($_POST['email'] ?? '');
            $phone = trim($_POST['phone'] ?? '');

            // Validate required data
            if (empty($name)) {
                sendResponse(false, 'Username is required', null, 400);
            }
            
            if (empty($email)) {
                sendResponse(false, 'Email is required', null, 400);
            }
            
            if (empty($phone)) {
                sendResponse(false, 'Phone number is required', null, 400);
            }

            // Validate data format
            if (!validateEmail($email)) {
                sendResponse(false, 'Invalid email format', null, 400);
            }

            if (!validatePhone($phone)) {
                sendResponse(false, 'Invalid phone number format', null, 400);
            }

            // Validate data length
            if (strlen($name) > 100) {
                sendResponse(false, 'Name too long (maximum 100 characters)', null, 400);
            }

            if (strlen($email) > 100) {
                sendResponse(false, 'Email too long (maximum 100 characters)', null, 400);
            }

            // Check for duplicate email
            $checkStmt = $pdo->prepare("SELECT id FROM users WHERE email = ?");
            $checkStmt->execute([$email]);
            if ($checkStmt->fetch()) {
                sendResponse(false, 'Email already exists', null, 409);
            }

            // Insert new user
            $stmt = $pdo->prepare("INSERT INTO users (name, email, phone) VALUES (?, ?, ?)");
            $stmt->execute([$name, $email, $phone]);
            
            $userId = $pdo->lastInsertId();
            logMessage("User created successfully with ID: " . $userId);

            sendResponse(true, 'User created successfully', [
                'user_id' => $userId,
                'name' => $name,
                'email' => $email
            ]);
            break;

        case 'read':
            // === Read all users ===
            logMessage("Processing READ users request");
            
            // Add search and pagination capability
            $search = $_GET['search'] ?? '';
            $page = max(1, (int)($_GET['page'] ?? 1));
            $limit = min(100, max(1, (int)($_GET['limit'] ?? 50))); // Maximum 100
            $offset = ($page - 1) * $limit;

            // Build query
            $whereClause = '';
            $params = [];
            
            if (!empty($search)) {
                $whereClause = "WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?";
                $searchTerm = "%$search%";
                $params = [$searchTerm, $searchTerm, $searchTerm];
            }

            // Count total
            $countStmt = $pdo->prepare("SELECT COUNT(*) as total FROM users $whereClause");
            $countStmt->execute($params);
            $totalUsers = $countStmt->fetch()['total'];

            // Fetch users
            $stmt = $pdo->prepare("
                SELECT id, name, email, phone, 
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                       DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
                FROM users 
                $whereClause
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ");
            
            $params[] = $limit;
            $params[] = $offset;
            $stmt->execute($params);
            $users = $stmt->fetchAll();

            logMessage("Retrieved " . count($users) . " users out of $totalUsers total");

            sendResponse(true, 'Data retrieved successfully', [
                'users' => $users,
                'pagination' => [
                    'current_page' => $page,
                    'total_users' => $totalUsers,
                    'users_per_page' => $limit,
                    'total_pages' => ceil($totalUsers / $limit)
                ]
            ]);
            break;

        case 'update':
            // === Update existing user ===
            logMessage("Processing UPDATE user request");
            
            $id = (int)($_POST['id'] ?? 0);
            $name = trim($_POST['name'] ?? '');
            $email = trim($_POST['email'] ?? '');
            $phone = trim($_POST['phone'] ?? '');

            // Validate data
            if ($id <= 0) {
                sendResponse(false, 'Invalid user ID', null, 400);
            }

            if (empty($name) || empty($email) || empty($phone)) {
                sendResponse(false, 'All fields are required', null, 400);
            }

            if (!validateEmail($email)) {
                sendResponse(false, 'Invalid email format', null, 400);
            }

            if (!validatePhone($phone)) {
                sendResponse(false, 'Invalid phone number format', null, 400);
            }

            // Check if user exists
            $checkStmt = $pdo->prepare("SELECT name, email FROM users WHERE id = ?");
            $checkStmt->execute([$id]);
            $currentUser = $checkStmt->fetch();
            
            if (!$currentUser) {
                sendResponse(false, 'User not found', null, 404);
            }

            // Check for duplicate email with other users
            $checkEmailStmt = $pdo->prepare("SELECT id FROM users WHERE email = ? AND id != ?");
            $checkEmailStmt->execute([$email, $id]);
            if ($checkEmailStmt->fetch()) {
                sendResponse(false, 'Email already used by another user', null, 409);
            }

            // Update user
            $stmt = $pdo->prepare("UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?");
            $stmt->execute([$name, $email, $phone, $id]);

            logMessage("User updated successfully. ID: $id");

            sendResponse(true, 'User data updated successfully', [
                'user_id' => $id,
                'old_email' => $currentUser['email'],
                'new_email' => $email
            ]);
            break;

        case 'delete':
            // === Delete user ===
            logMessage("Processing DELETE user request");
            
            $id = (int)($_POST['id'] ?? $_GET['id'] ?? 0);

            if ($id <= 0) {
                sendResponse(false, 'Invalid user ID', null, 400);
            }

            // Check if user exists and get their data
            $checkStmt = $pdo->prepare("SELECT name, email FROM users WHERE id = ?");
            $checkStmt->execute([$id]);
            $user = $checkStmt->fetch();
            
            if (!$user) {
                sendResponse(false, 'User not found', null, 404);
            }

            // Delete user
            $stmt = $pdo->prepare("DELETE FROM users WHERE id = ?");
            $stmt->execute([$id]);

            logMessage("User deleted successfully. ID: $id, Name: " . $user['name']);

            sendResponse(true, 'User "' . $user['name'] . '" deleted successfully', [
                'deleted_user' => [
                    'id' => $id,
                    'name' => $user['name'],
                    'email' => $user['email']
                ]
            ]);
            break;

        case 'get_single':
            // === Get single user ===
            logMessage("Processing GET SINGLE user request");
            
            $id = (int)($_GET['id'] ?? 0);

            if ($id <= 0) {
                sendResponse(false, 'Invalid user ID', null, 400);
            }

            $stmt = $pdo->prepare("
                SELECT id, name, email, phone, 
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at,
                       DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s') as updated_at
                FROM users WHERE id = ?
            ");
            $stmt->execute([$id]);
            $user = $stmt->fetch();

            if (!$user) {
                sendResponse(false, 'User not found', null, 404);
            }

            logMessage("Single user retrieved successfully. ID: $id");

            sendResponse(true, 'User data retrieved successfully', ['user' => $user]);
            break;

        case 'stats':
            // === System statistics ===
            logMessage("Processing STATS request");
            
            // Count users
            $totalStmt = $pdo->query("SELECT COUNT(*) as total FROM users");
            $totalUsers = $totalStmt->fetch()['total'];

            // Count users added today
            $todayStmt = $pdo->query("SELECT COUNT(*) as today FROM users WHERE DATE(created_at) = CURDATE()");
            $todayUsers = $todayStmt->fetch()['today'];

            // Count users added this week
            $weekStmt = $pdo->query("SELECT COUNT(*) as week FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)");
            $weekUsers = $weekStmt->fetch()['week'];

            // Last added user
            $lastUserStmt = $pdo->query("SELECT name, email, created_at FROM users ORDER BY created_at DESC LIMIT 1");
            $lastUser = $lastUserStmt->fetch();

            sendResponse(true, 'Statistics retrieved successfully', [
                'total_users' => $totalUsers,
                'users_today' => $todayUsers,
                'users_this_week' => $weekUsers,
                'last_user' => $lastUser
            ]);
            break;

        case 'get_api_source':
            // === Return API source code for frontend display ===
            logMessage("Processing GET API SOURCE request");
            
            sendResponse(true, 'Source code retrieved successfully', [
                'source_code' => file_get_contents(__FILE__),
                'file_size' => filesize(__FILE__),
                'last_modified' => date('Y-m-d H:i:s', filemtime(__FILE__))
            ]);
            break;

        case 'test_connection':
            // === Test connection ===
            logMessage("Processing TEST CONNECTION request");
            
            sendResponse(true, 'Connection working successfully', [
                'server_time' => date('Y-m-d H:i:s'),
                'php_version' => PHP_VERSION,
                'database_connection' => 'Connected',
                'memory_usage' => memory_get_usage(true),
                'api_version' => '1.0.0'
            ]);
            break;

        case '':
        case null:
            // === API Information (when accessed directly) ===
            logMessage("API accessed directly - showing information");
            
            sendResponse(true, 'User Management API - Genetic Invent Demo', [
                'api_version' => '1.0.0',
                'server_time' => date('Y-m-d H:i:s'),
                'website' => 'glconnectionbuilder1.com',
                'database' => 'u419999707_Demo',
                'available_actions' => [
                    'create' => 'Create new user (POST)',
                    'read' => 'Get all users (GET)',
                    'update' => 'Update existing user (POST)',
                    'delete' => 'Delete user (POST/GET)',
                    'get_single' => 'Get single user by ID (GET)',
                    'stats' => 'Get system statistics (GET)',
                    'test_connection' => 'Test API connection (GET)',
                    'get_api_source' => 'Get API source code (GET)'
                ],
                'examples' => [
                    'Test connection' => '?action=test_connection',
                    'Get all users' => '?action=read',
                    'Get statistics' => '?action=stats'
                ],
                'status' => 'API is running successfully'
            ]);
            break;

        default:
            logMessage("Unknown action requested: " . $action, 'ERROR');
            sendResponse(false, 'Unknown action. Available actions: create, read, update, delete, get_single, stats, get_api_source, test_connection', null, 400);
    }

} catch (PDOException $e) {
    // Database error
    logMessage("Database error: " . $e->getMessage(), 'ERROR');
    
    // More detailed error information for debugging
    $errorDetails = [
        'error_code' => $e->getCode(),
        'error_message' => $e->getMessage(),
        'database_config' => [
            'host' => DB_HOST,
            'database' => DB_NAME,
            'user' => DB_USER,
            'port' => DB_PORT
        ]
    ];
    
    // Add additional error info if available
    if ($e->errorInfo) {
        $errorDetails['error_info'] = $e->errorInfo;
    }
    
    sendResponse(false, 'Database connection failed. Please check database credentials and server status.', $errorDetails, 500);

} catch (Exception $e) {
    // General error
    logMessage("General error: " . $e->getMessage(), 'ERROR');
    
    sendResponse(false, $e->getMessage(), [
        'error_code' => $e->getCode()
    ], 400);

} catch (Throwable $e) {
    // Fatal error
    logMessage("Fatal error: " . $e->getMessage(), 'ERROR');
    
    sendResponse(false, 'Fatal system error', [
        'error_message' => $e->getMessage(),
        'error_file' => $e->getFile(),
        'error_line' => $e->getLine()
    ], 500);
}
?> 