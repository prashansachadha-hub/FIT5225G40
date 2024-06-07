// Configuration
const region = 'us-east-1'; 
const userPoolId = 'us-east-1_yGMThNzou';
const clientId = '7kv0atdqrjpjmfn34ohp7r1h2m';
const clientSecret = '1u0bb9t56qer70lqs1p0bvbkdvshnb01jfndktvc58bls0kq4chk'; // e.g., 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
const redirectUri = 'https://d2ellcpag6d7ln.cloudfront.net'; // e.g., 'http://localhost:3000'
const cognitoDomain = 'fit5225-g40-2.auth.us-east-1.amazoncognito.com'; // e.g., 'your-app.auth.us-east-1.amazoncognito.com'


function getCognitoSignInUrl() {
    const url = `https://fit5225-g40-2.auth.us-east-1.amazoncognito.com/login?client_id=7kv0atdqrjpjmfn34ohp7r1h2m&response_type=code&scope=email+openid+phone&redirect_uri=https%3A%2F%2Fd2ellcpag6d7ln.cloudfront.net`;
    return url;
}


document.getElementById('sign-in-button').addEventListener('click', () => {
    window.location.href = getCognitoSignInUrl();
});


document.getElementById('sign-out-button').addEventListener('click', () => {

    window.localStorage.removeItem('access_token');
    window.localStorage.removeItem('id_token');
    window.localStorage.removeItem('refresh_token');
    window.location.href = '/';
});


function isAuthenticated() {
    const idToken = window.localStorage.getItem('id_token');
    return idToken !== null;
}


function parseUrlParams() {
    const queryString = window.location.search.substring(1);
    const params = {};
    queryString.split('&').forEach(item => {
        const [key, value] = item.split('=');
        params[key] = decodeURIComponent(value);
    });
    return params;
}


async function exchangeCodeForTokens(code) {
    const url = `https://${cognitoDomain}/oauth2/token`;
    const body = `grant_type=authorization_code&client_id=${clientId}&code=${code}&redirect_uri=${redirectUri}`;
    const headers = new Headers({
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + btoa(`${clientId}:${clientSecret}`)
    });

    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: body
    });

    const data = await response.json();
    return data;
}

// Handle authentication on page load
window.onload = async () => {
    const params = parseUrlParams();
    if (params.code) {
        try {
            const tokens = await exchangeCodeForTokens(params.code);
            window.localStorage.setItem('access_token', tokens.access_token);
            window.localStorage.setItem('id_token', tokens.id_token);
            window.localStorage.setItem('refresh_token', tokens.refresh_token);
            window.location.search = ''; 
        } catch (error) {
            console.error('Error exchanging code for tokens:', error);
        }
    }

    if (isAuthenticated()) {
        document.getElementById('sign-in-button').style.display = 'none';
        document.getElementById('sign-out-button').style.display = 'block';
        document.getElementById('upload-container').style.display = 'block';
        document.getElementById('query-container').style.display = 'block';
    
        // Add event listeners for buttons
        document.getElementById('upload-button').addEventListener('click', uploadImage);
        document.getElementById('search-button').addEventListener('click', submitQuery);

    } else {
        window.location.href = getCognitoSignInUrl();
    }
};