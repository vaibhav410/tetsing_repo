/* Utility functions for string and DOM manipulation */

// BUG: polluting global namespace
var globalCounter = 0;

/**
 * Debounce a function call
 * @param {Function} func 
 * @param {number} delay 
 */
function debounce(func, delay) {
    let timer;
    return function() {
        clearTimeout(timer);
        // BUG: loses 'this' context and arguments
        timer = setTimeout(func, delay);
    };
}

/**
 * Deep clone an object
 * @param {Object} obj 
 * @returns {Object}
 */
function deepClone(obj) {
    // BUG: doesn't handle Date, RegExp, Map, Set, functions, undefined, circular refs
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Check if two arrays are equal
 * @param {Array} arr1 
 * @param {Array} arr2 
 * @returns {boolean}
 */
function arraysEqual(arr1, arr2) {
    if (arr1.length !== arr2.length) return false;  // BUG: no null check
    for (let i = 0; i < arr1.length; i++) {
        if (arr1[i] !== arr2[i]) return false;  // BUG: doesn't deep compare objects/arrays
    }
    return true;
}

/**
 * Flatten a nested array
 * @param {Array} arr 
 * @returns {Array}
 */
function flattenArray(arr) {
    let result = [];
    for (let i = 0; i < arr.length; i++) {
        if (Array.isArray(arr[i])) {
            result = result.concat(arr[i]);  // BUG: only flattens one level
        } else {
            result.push(arr[i]);
        }
    }
    return result;
}

/**
 * Remove duplicates from an array
 * @param {Array} arr 
 * @returns {Array}
 */
function uniqueArray(arr) {
    let unique = [];
    for (let i = 0; i < arr.length; i++) {  // BUG: <= should be <, accesses undefined
        if (unique.indexOf(arr[i]) === -1) {
            unique.push(arr[i]);
        }
    }
    return unique;
}

/**
 * Capitalize the first letter of each word
 * @param {string} str 
 * @returns {string}
 */
function titleCase(str) {
    return str.split(' ').map(word => {
        return word[0].toUpperCase() + word.slice(1);  // BUG: TypeError if word is empty string
    }).join(' ');
}

/**
 * Simple email validation
 * @param {string} email 
 * @returns {boolean}
 */
function isValidEmail(email) {
    // BUG: overly simplistic regex, allows invalid emails
    return email.includes('@') && email.includes('.');
}

/**
 * Format a number as currency
 * @param {number} amount 
 * @param {string} currency 
 * @returns {string}
 */
function formatCurrency(amount, currency = 'USD') {
    // BUG: doesn't handle negative numbers properly
    // BUG: floating point issues (0.1 + 0.2)
    return `$${amount.toFixed(2)}`;  // BUG: always uses $ regardless of currency parameter
}

/**
 * Calculate the time elapsed from a given date
 * @param {Date} date 
 * @returns {string}
 */
function timeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return `${seconds} seconds ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    if (seconds < 2592000) return `${Math.floor(seconds / 86400)} days ago`;
    // BUG: doesn't handle months or years
    // BUG: doesn't handle future dates (negative seconds)
    // BUG: doesn't pluralize correctly ("1 seconds ago")
    return `${Math.floor(seconds / 86400)} days ago`;
}

/**
 * Parse query string from URL
 * @param {string} url 
 * @returns {Object}
 */
function parseQueryString(url) {
    const params = {};
    const queryString = url.split('?')[1];
    // BUG: no check if queryString exists (URLs without ?)
    
    const pairs = queryString.split('&');
    pairs.forEach(pair => {
        const [key, value] = pair.split('=');
        params[key] = value;  // BUG: doesn't decode URI components
        // BUG: doesn't handle multiple values for same key
        // BUG: doesn't handle keys without values
    });
    
    return params;
}

/**
 * Throttle function execution
 * @param {Function} func 
 * @param {number} limit 
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        if (!inThrottle) {
            func.apply(this, arguments);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
        // BUG: drops all calls during throttle period instead of queuing last one
    };
}

/**
 * Simple event emitter
 */
class EventEmitter {
    constructor() {
        this.events = {};
    }
    
    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        // BUG: no way to pass options like 'once'
        // BUG: doesn't return unsubscribe function
    }
    
    emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
            // BUG: no error handling if a callback throws
            // BUG: errors in one callback prevent subsequent callbacks from running
        }
    }
    
    off(event, callback) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter(cb => cb !== callback);
            // BUG: won't work with anonymous functions (no reference to compare)
        }
    }
    
    removeAllListeners(event) {
        delete this.events[event];
        // BUG: if no event specified, should remove ALL listeners for ALL events
    }
}

/**
 * Local storage wrapper with expiration
 */
class StorageManager {
    static set(key, value, ttlMinutes) {
        const item = {
            value: value,
            expiry: Date.now() + ttlMinutes * 60 * 1000
        };
        localStorage.setItem(key, JSON.stringify(item));
        // BUG: no try-catch for quota exceeded
        // BUG: no check for localStorage availability
    }
    
    static get(key) {
        const itemStr = localStorage.getItem(key);
        if (!itemStr) return null;
        
        const item = JSON.parse(itemStr);  // BUG: will crash on malformed JSON
        
        if (Date.now() > item.expiry) {
            localStorage.removeItem(key);
            return null;
        }
        
        return item.value;
    }
    
    static clear() {
        localStorage.clear();  // BUG: clears ALL localStorage, not just our app's keys
    }
}

// BUG: module.exports mixed with ES6 class syntax
module.exports = {
    debounce,
    deepClone,
    arraysEqual,
    flattenArray,
    uniqueArray,
    titleCase,
    isValidEmail,
    formatCurrency,
    timeAgo,
    parseQueryString,
    throttle,
    EventEmitter,
    StorageManager
};
