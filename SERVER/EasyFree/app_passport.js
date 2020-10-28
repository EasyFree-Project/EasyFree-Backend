var express = require('express');
var session = require('express-session');
var http = require('http');
var bodyParser = require('body-parser');
var MySQLStore = require('express-mysql-session')(session);
var bkfd2Password = require("pbkdf2-password");
var passport = require('passport')
var LocalStrategy = require('passport-local').Strategy;
var hasher = bkfd2Password();
var mysql = require('mysql');
var conn = mysql.createConnection({
    host:'220.90.200.176',
    user: 'multi',
    password: 'multi!)@(',
    database: 'EasyFree'
});
conn.connect();
var app_passport = express();
app_passport.use(bodyParser.urlencoded({ extended: false }));
app_passport.use(session({
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
app_passport.use(passport.initialize());
app_passport.use(passport.session());
app_passport.use(bodyParser.json());

app_passport.get('/', function(err, res){
    res.send('Welcome EasyFree Server!');
});

// 세션 관련, 로그인에 성공했을 경우 done의 실행으로 user데이터가 넘어오고 실행됨.
passport.serializeUser(function(user, done) {
    console.log('serializeUser', user);
    done(null, user.authId);
});

// 세션에 로그인 정보가 저장되었을 경우 실행됨
passport.deserializeUser(function(id, done) {
    console.log('deserializeUser', id);
    var sql = 'SELECT * FROM Member WHERE authId=?';
    conn.query(sql, [id], function(err, results){
        if(err){
            console.log(err);
            done('There is no user.');
        } else {
            done(null,results[0]);
        }
    });
});

passport.use(new LocalStrategy(  // passport를 사용함에 있어서 로컬 전략을 사용하겠다는 객체생성
    function(username, password, done){
        var uname = username;
        var pwd = password;
        var sql = 'SELECT * FROM Member WHERE authId=?';
        conn.query(sql, ['local:'+uname],function(err, results){
            if(err){
                return done('There is no user.');
            }
            var user = results[0];
            return hasher({password: pwd, salt: user.salt}, function (err, pass, salt, hash) {
                if (hash === user.password) {
                    console.log('LocalStrategy', user);
                    done(null, user);
                } else {
                    done(null, false);
                }
            });
        });
    }
));

app_passport.post('/auth/login', passport.authenticate('local',
    { //successRedirect: '/welcome',
        failureRedirect: '/auth/failLogin', failureFlash: false
    }),
    function(req, res){
        req.session.save(function(){
            var success = {
                "statusCode": 200,
                "message": "로그인 성공"
            };
            res.send(success);
        })
    }
);

app_passport.get('/auth/failLogin', function(req, res){
    var fail = {
        "statusCode": 400,
        "message": "로그인 실패"
    };
    res.send(fail);
});


app_passport.post('/auth/register', function(req, res){
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
                res.send(fail);
            } else {
                req.login(user, function(err){
                    req.session.save(function(){
                        var success = {
                            "statusCode": 200,
                            "message": "회원가입 성공"
                        };
                        res.send(success);
                    });
                })
            }
        });
    });
});

app_passport.listen(3003, function(){
    console.log("Connected 3003 port!!!");
});