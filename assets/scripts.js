// assets/scripts.js

// Ensure the clientside object exists
window.dash_clientside = window.dash_clientside || {};

// Namespace for our UI callbacks
window.dash_clientside.ui_callbacks = {
    // --- Function to initialize the chat hover effect ---
    initChatHover: function(_) {
        // Prevent re-initializing the listeners
        if (window.chatHoverInitialized) {
            return window.dash_clientside.no_update;
        }
        window.chatHoverInitialized = true;

        const chatWindow = document.getElementById('chat-window-container');
        if (!chatWindow) return '';

        let timeoutId = null;
        const activateChat = () => {
            clearTimeout(timeoutId);
            chatWindow.classList.add('chat-active');
        };
        const deactivateChat = () => {
            timeoutId = setTimeout(() => {
                chatWindow.classList.remove('chat-active');
            }, 5000); // 5-second delay before hiding
        };

        chatWindow.addEventListener('mouseenter', activateChat);
        chatWindow.addEventListener('mouseleave', deactivateChat);
        
        // Initially activate the chat window and set a timer to deactivate it
        activateChat();
        deactivateChat();

        return window.dash_clientside.no_update;
    },

    // --- Function to auto-scroll the chat history ---
    scrollChat: function(children) {
        const chatHistory = document.getElementById('chat-history');
        if (chatHistory) {
            // Use a small timeout to ensure the new message is rendered in the DOM
            // before we calculate the scroll height.
            setTimeout(function() {
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }, 50);
        }
        // Tell Dash that no component property needs to be updated.
        return window.dash_clientside.no_update;
    }
};

// Inject lightweight CSS to limit the opened dropdown menu height for dropdowns using
// dropdownClassName='compact-dropdown-menu' so only ~2 rows are visible and a scrollbar appears.
(function injectCompactDropdownCss() {
    if (document.getElementById('compact-dropdown-css')) return;
    var css = `
    /* Target Dash/React dropdown menu container when dropdownClassName is set */
    .compact-dropdown-menu {
        max-height: 64px !important; /* ~2 options visible (adjust as needed) */
        overflow-y: auto !important;
    }
    /* Some Dash/react-select versions place the class on a parent; also target menu elements */
    .compact-dropdown-menu .Select-menu-outer,
    .compact-dropdown-menu .Select-menu,
    .compact-dropdown-menu .VirtualizedSelectMenu {
        max-height: 64px !important;
        overflow-y: auto !important;
    }
    `;
    var style = document.createElement('style');
    style.id = 'compact-dropdown-css';
    style.type = 'text/css';
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);
})();
