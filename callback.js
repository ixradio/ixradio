var http = require('http')

http.createServer(function(req, res){
    res.sendStatus(200);
    res.end();
}).listen(5000);
