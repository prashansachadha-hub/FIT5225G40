import { createBrowserRouter } from 'react-router-dom'
import App from "./App"
import HomePage from './pages/HomePage/HomePage'
import NotFoundPage from './pages/NotFoundPage/NotFoundPage'
import RequireAuth from './authLogics/RequireAuth'
import LoginSuccess from './pages/LoginSuccess/LoginSuccess'

export const router = createBrowserRouter([
    {
        path: "/",
        element: <App />,
        children: [
            { path: "", element: <RequireAuth><HomePage /></RequireAuth> },
            { path: "*", element: <RequireAuth><NotFoundPage /></RequireAuth> },
            { path: "login_success", element: <LoginSuccess/>}
        ]
    }
])