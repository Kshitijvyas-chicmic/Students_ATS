/**
 * API Configuration
 * 
 * Using 127.0.0.1 instead of localhost to avoid potential name resolution issues.
 */

const API_BASE_URL = 'https://student-ats-2.onrender.com';

// window.API_BASE_URL = API_BASE_URL;
// console.log("ATS App initialized with API_BASE_URL:", window.API_BASE_URL);
window.API_BASE_URL =
    location.hostname === "localhost"
        ? "http://127.0.0.1:8000"
        : "https://student-ats-2.onrender.com";

console.log("API_BASE_URL:", window.API_BASE_URL);