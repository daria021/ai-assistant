import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { postEvent } from '@telegram-apps/sdk';

function useBackButtonVisibility() {
     const location = useLocation();

     useEffect(() => {
         // Set is_visible to false for the home page ('/') and true otherwise.
         const isVisible = location.pathname !== "/";
         postEvent('web_app_setup_back_button', { is_visible: isVisible });
     }, [location.pathname]);
}

export default useBackButtonVisibility;
