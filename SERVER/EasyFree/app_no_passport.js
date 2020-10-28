var express = require('express');
var session = require('express-session');
var http = require('http');
var bodyParser = require('body-parser');
var MySQLStore = require('express-mysql-session')(session);
var bkfd2Password = require("pbkdf2-password");
var hasher = bkfd2Password();
var mysql = require('mysql');
var conn = mysql.createConnection({
    host:'220.90.200.176',
    user: 'multi',
    password: 'multi!)@(',
    database: 'EasyFree'
});
conn.connect();
var app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(session({
    secret: 'happy',
    resave: false,
    saveUninitialized: true,
    store: new MySQLStore({
        host: '220.90.200.176',
        port: 3306,
        user: 'multi',
        password: 'multi!)@(',
        database: 'EasyFree'
    })
}));

app.get('/', function(err, res){
    res.send('Welcome EasyFree Server!');
});

app.post('/auth/login', function(req, res){
    console.log(req.body);
    var uname = req.body.username;
    var pwd = req.body.password;
    var sql = 'SELECT * FROM Member WHERE authId=?';
    conn.query(sql, ['local:'+uname],function(err, results){
        if(err){
            console.log(err);
            res.status(500).send('Internal Server Error');
        }
        var user = results[0];
        if(!user){
            var fail = {
                "statusCode": 407,
                "message": "유저정보가 존재하지 않습니다."
            };
            return res.status(407).send(fail);
        }
        return hasher({password: pwd, salt: user.salt}, function (err, pass, salt, hash) {
            if (hash === user.password) {
                console.log('Login', user);
                var success = {
                    "statusCode": 200,
                    "message": "로그인 성공"
                };
                res.status(200).send(success);
            } else {
                var fail = {
                    "statusCode": 403,
                    "message": "잘못된 비밀번호입니다."
                };
                res.status(403).send(fail);
            }
        });
    });
});

app.post('/auth/register', function(req, res){
    console.log(req.body);
    hasher({password:req.body.password}, function(err, pass, salt, hash){
        var user = {
            authId:'local:'+req.body.username,
            username:req.body.username,
            password:hash,
            salt:salt,
            displayName:req.body.displayName
        };
        var sql = 'INSERT INTO Member SET ?';
        conn.query(sql, user, function(err, results){
            if(err){
                console.log(err);
                var fail = {
                    "statusCode": 500,
                    "message": "회원가입 실패"
                };
                res.status(500).send(fail);
            } else {
                req.session.save(function(){
                    var success = {
                        "statusCode": 200,
                        "message": "회원가입 성공"
                    };
                    res.status(200).send(success);
                });
            }
        });
    });
});

app.post('/request_test', function(req, res){
    res.send(req.body);
});


app.listen(3003, function(){
    console.log("Connected 3003 port!!!");
});