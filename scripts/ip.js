const http = require('http');
const fs = require('fs');

const server = http.createServer((req, res) => {
    // Getting the IP address of the user
    const ip = req.connection.remoteAddress;
    
    // Logging the IP address to console
    console.log('User IP:', ip);
    
    // Saving the IP address to a text file
    fs.appendFile('user_ips.txt', ip + '\n', (err) => {
        if (err) throw err;
        console.log('User IP saved to file.');
    });

    res.end('IP logged successfully!');
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
