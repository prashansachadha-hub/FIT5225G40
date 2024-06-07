AWS.config.region = 'us-east-1'; 

var poolData = {
    UserPoolId: 'us-east-1_yGMThNzou', 
    ClientId: '7kv0atdqrjpjmfn34ohp7r1h2m'
};

var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);


function redirectToSignUp() {


    var signUpUrl = `https://fit5225-g40-2.auth.us-east-1.amazoncognito.com/login?client_id=7kv0atdqrjpjmfn34ohp7r1h2m&response_type=code&scope=email+openid+phone&redirect_uri=https%3A%2F%2Fd2ellcpag6d7ln.cloudfront.net`;
    window.location.href = signUpUrl;
}

function exchangeCodeForTokens(code) {
    var cognitoDomain = 'fit5225-g40-2.auth.us-east-1.amazoncognito.com';
    var clientId = poolData.ClientId;
    var redirectUri = window.location.href.split('?')[0];
    var encMessage = 'N2t2MGF0ZHFyanBqbWZuMzRvaHA3cjFoMm06MXUwYmI5dDU2cWVyNzBscXMxcDBidmJrZHZzaG5iMDFqZm5ka3R2YzU4YmxzMGtxNGNoaw==';

    var tokenUrl = `https://${cognitoDomain}/oauth2/token`;
    var body = `grant_type=authorization_code&client_id=${clientId}&code=${code}&redirect_uri=${redirectUri}`;

    fetch(tokenUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': `Basic ${encMessage}`
            
        },
        body: body
    })
    .then(response => response.json())
    .then(data => {
        console.log("Token Exchange Response:", data);
        if (data.access_token) {
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('idToken', data.id_token);
            localStorage.setItem('refreshToken', data.refresh_token);
            console.log("Tokens stored in localStorage.");
        }

        window.location.href = redirectUri;
    })
    .catch(error => console.error('Error:', error));
}


function parseAuthCode() {
    var urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('code')) {
        var code = urlParams.get('code');
        console.log("Auth code: ", code);
        exchangeCodeForTokens(code);
    }
}

window.onload = function () {
    if (!localStorage.getItem('accessToken')) {
        parseAuthCode();
        if (!localStorage.getItem('accessToken')) {
            redirectToSignUp();
        }
    }
};


