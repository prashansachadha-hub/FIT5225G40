import * as React from 'react';
import styles from "./LoginSuccess.module.scss"
import { useNavigate } from 'react-router-dom';

function LoginSuccess() {
    const navigate = useNavigate();

    React.useEffect(()=>{
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        const accessToken = params.get('access_token');
        const idToken = params.get('id_token');

        if (accessToken && idToken) {
            sessionStorage.setItem('accessToken', accessToken);
            sessionStorage.setItem('idToken', idToken);
            sessionStorage.setItem('isAuth', 'true');
            navigate('/');
        }
    }, [])
    
    return null;
}

export default LoginSuccess;