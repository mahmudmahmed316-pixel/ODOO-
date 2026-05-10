/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { onMounted, onRendered } from "@odoo/owl";

patch(NavBar.prototype, {
    setup() {
        super.setup();

        onMounted(() => {
            // Check immediately on mount
            this._forceShowHomeMenu();
        });

        onRendered(() => {
            // Re-check on every render to ensure it stays open if we are at home
            this._forceShowHomeMenu();
        });
    },

    _forceShowHomeMenu() {
        const currentHash = window.location.hash;
        // If we are at the root or home, ensure the menu is open
        if (!currentHash || currentHash === "#home" || currentHash === "#") {
            const dashboard = document.querySelector('.o_premium_apps_dashboard');
            const appsMenuBtn = document.querySelector('.o_navbar_apps_menu button');

            // If the dashboard isn't showing, click the button to show it
            if (appsMenuBtn && (!dashboard || !dashboard.classList.contains('show'))) {
                appsMenuBtn.click();
            }
        }
    },

    /**
     * Override app click to ensure menu closes correctly
     */
    onNavBarDropdownItemSelection(app) {
        super.onNavBarDropdownItemSelection(app);
        // Odoo standard handles closing, but we ensure it.
    }
});
