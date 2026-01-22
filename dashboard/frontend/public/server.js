const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = 3000;
const PUBLIC_DIR = __dirname;
const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    // Log request
    const timestamp = new Date().toISOString().substr(11, 8);
    console.log(`[${timestamp}] ${req.method} ${req.url}`);
    
    let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'dashboard.html' : req.url);
    
    // Security: prevent directory traversal
    const resolvedPath = path.resolve(filePath);
    if (!resolvedPath.startsWith(PUBLIC_DIR)) {
        console.log(`  → Blocked (directory traversal)`);
        res.writeHead(403, { 'Content-Type': 'text/plain' });
        res.end('403 Forbidden');
        return;
    }
    
    // Add CORS headers for API calls
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            // File not found, serve dashboard.html instead
            filePath = path.join(PUBLIC_DIR, 'dashboard.html');
        }
        
        fs.readFile(filePath, (err, data) => {
            if (err) {
                console.log(`  → 404 Not Found`);
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                res.end('404 Not Found');
                return;
            }
            
            const ext = path.extname(filePath).toLowerCase();
            const contentType = mimeTypes[ext] || 'application/octet-stream';
            
            res.writeHead(200, { 
                'Content-Type': contentType,
                'Content-Length': data.length,
                'Cache-Control': 'no-cache'
            });
            res.end(data);
            console.log(`  → 200 OK (${data.length} bytes)`);
        });
    });
});

// Error handling
server.on('error', (err) => {
    console.error('❌ Server error:', err.message);
    if (err.code === 'EADDRINUSE') {
        console.error(`Port ${PORT} is already in use`);
        process.exit(1);
    }
});

process.on('uncaughtException', (err) => {
    console.error('❌ Uncaught exception:', err.message);
    process.exit(1);
});

process.on('unhandledRejection', (reason) => {
    console.error('❌ Unhandled rejection:', reason);
    process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n📛 Server shutting down...');
    server.close(() => {
        console.log('✓ Server stopped');
        process.exit(0);
    });
    setTimeout(() => {
        console.error('Force shutting down');
        process.exit(1);
    }, 5000);
});

// Start server
server.listen(PORT, '0.0.0.0', () => {
    const hostname = 'localhost';
    console.log('\n╔════════════════════════════════════════════╗');
    console.log('║  ✓ Dashboard Server Running                ║');
    console.log('╚════════════════════════════════════════════╝\n');
    console.log(`📍 URL: http://${hostname}:${PORT}/dashboard.html`);
    console.log(`📂 Dir: ${PUBLIC_DIR}`);
    console.log(`🖥️  Node: ${process.version}`);
    console.log(`⏰ Time: ${new Date().toISOString()}\n`);
    console.log('Ready to accept connections...\n');
});
