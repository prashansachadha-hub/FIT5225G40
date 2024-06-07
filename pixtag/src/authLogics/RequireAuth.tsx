import { ReactNode, useEffect } from "react";

interface Props {
    children: ReactNode;
}

const RequireAuth: React.FC<Props> = ({ children }) => {
    const isAuth = sessionStorage.getItem("isAuth") === "true"
    useEffect(() => {
        if (!isAuth) {
            window.location.href = process.env.REACT_APP_AWS_COGNITO!;
        }
    }, []);

    if (!isAuth) return null;

    return (<>{children}</>)
}

export default RequireAuth;
