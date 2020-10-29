var express = require('express');
var session = require('express-session');
var http = require('http');
var bodyParser = require('body-parser');
var MySQLStore = require('express-mysql-session')(session);
var bkfd2Password = require("pbkdf2-password");
var hasher = bkfd2Password();
var {PythonShell} = require('python-shell');
var moment = require('moment');
require('moment-timezone');
moment.tz.setDefault("Asia/Seoul");
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

app.post('/request_test', function(req, res){
    res.send(req.body);
});

app.post('/auth/login', function(req, res){
    console.log(req.body);
    var uname = req.body.username;
    var pwd = req.body.password;
    var sql = 'SELECT * FROM member WHERE authId=?';
    conn.query(sql, ['local:'+uname],function(err, results){
        if(err){
            console.log(err);
            res.status(500).send('Internal Server Error');
        }
        var user = results[0];
        if(!user){
            var fail = {
                "statusCode": 407,
                "message": "존재하지 않는 유저입니다."
            };
            return res.status(407).send(fail);
        }
        return hasher({password: pwd, salt: user.salt}, function (err, pass, salt, hash) {
            if (hash === user.password) {
                console.log('Login', user);
                var success = {
                    "statusCode": 200,
                    "message": "로그인 성공",
                    "data": {
                        "member_idx": user.member_idx
                    }
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
        var sql = 'INSERT INTO member SET ?';
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
                    var sql = 'SELECT * FROM member WHERE authId=?';
                    conn.query(sql, [user.authId],function(err, results) {
                        var success = {
                            "statusCode": 200,
                            "message": "회원가입 성공",
                            "data": {
                                "member_idx": results[0].member_idx
                            }
                        };
                        res.status(200).send(success);
                    });
                });
            }
        });
    });
});

app.get('/product/:category_number', function(req, res) {
    console.log(req.params.category_number);
    var category_number = req.params.category_number;
    var sql = 'SELECT * FROM product WHERE category_number=?';
    conn.query(sql, [category_number], function (err, results) {
        if (err) {
            console.log(err);
            res.status(500).send('Internal Server Error');
        }
        if (!results[0]) {
            var fail = {
                "statusCode": 407,
                "message": "존재하지 않는 카테고리입니다."
            };
            return res.status(407).send(fail);
        }
        var success = {
            "statusCode": 200,
            "message": "카테고리 검색 성공",
            "data": {
                "item": results
            }
        };
        res.status(200).send(success);
    });
});

app.post('/model', function(req, res){
    console.log(req.body);
    var photo = req.body.photo;
    var options = {
        mode: 'text',
        encoding: 'utf8',
        // pythonPath: "C:/Python/Python36/python.exe",
        pythonOptions: ['-u'],
        // scriptPath: 'C:/Users/ehhah/dev/NLP_workspace/EasyFree/EasyFree-Backend/SERVER/EasyFree/Whaleling/Whaleling/predict_region.py',
        args: [photo]
    };
    PythonShell.run('model_temp.py', options, function (err, results) {
        if (err){
            console.log(err);
            res.status(500).send('Internal Server Error');
        }
        var success = {
            "statusCode": 200,
            "message": "모델 실행 성공",
            "data": {
                "result": results
            }
        };
        res.status(200).send(success);
    });
});

app.post('/purchase',function(req, res){
    console.log(req.body);
    var data = req.body.data[0];
    var time = moment().format('YYYY-MM-DD HH:MM:SS');
    console.log(time)
    var purchase_list = {
        member_idx:req.body.member_idx,
        product_number:data.product_number,
        product_count:data.product_count,
        purchase_date:time
    };
    var sql = 'INSERT INTO purchase SET ?';
    conn.query(sql, purchase_list, function(err, results) {
        if (err) {
            console.log(err);
            var fail = {
                "statusCode": 500,
                "message": "테이블 저장 실패"
            };
            res.status(500).send(fail);
        } else {
            var success = {
                "statusCode": 200,
                "message": "테이블 저장 성공",
            };
            res.status(200).send(success);
        }
    });
});

app.listen(3003, function(){
    console.log("Connected 3003 port!!!");
});