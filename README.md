# Student Course Feedback Management System

A simple, minimalistic frontend-only web application for managing student course feedback using HTML, CSS, and JavaScript.

## Features

- **Simple Login System**: Email and password login with simulated authentication
- **Feedback Form**: Submit feedback with course name, rating (1-5), and comments
- **Feedback Display**: View all submitted feedback in a clean, organized list
- **Local Storage**: All data is stored locally in the browser using localStorage
- **Clear Feedback**: Remove all feedback with a single click
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Clean, minimalistic design with smooth animations and hover effects

## File Structure

```
/
├── index.html      # Main feedback page with form and display
├── login.html      # Login page
├── styles.css      # All styling (modern, minimalistic design)
├── app.js          # JavaScript logic for feedback management
└── README.md       # This file
```

## How to Use

1. **Login**: 
   - Open `login.html` in your browser
   - Enter any email and password (no real authentication)
   - Click "Login" to proceed

2. **Submit Feedback**:
   - Fill in the course name
   - Select a rating (1-5)
   - Write your comments
   - Click "Submit Feedback"

3. **View Feedback**:
   - All submitted feedback appears below the form
   - Newest feedback appears first

4. **Clear Feedback**:
   - Click "Clear All Feedback" to remove all entries
   - Confirm the action in the popup

5. **Logout**:
   - Click the "Logout" button to return to the login page

## Technical Details

- **No Backend Required**: Everything runs in the browser
- **localStorage**: Data persists between sessions (per browser)
- **No External Dependencies**: Pure HTML, CSS, and JavaScript
- **Responsive**: Mobile-friendly design
- **Modern Styling**: Gradient backgrounds, soft shadows, rounded corners

## Browser Compatibility

Works in all modern browsers that support:
- HTML5
- CSS3
- ES6 JavaScript
- localStorage API

## Notes

- Data is stored locally in your browser and will persist until you clear browser data or use the "Clear All Feedback" button
- No actual authentication is performed - the login is simulated for demonstration purposes
- Each browser session is independent - feedback won't sync between devices

## Color Palette

- Primary Gradient: Purple to Blue (#667eea to #764ba2)
- Background: Light gray (#f9f9f9)
- Text: Dark gray (#333)
- Accent: Success green (#4caf50), Danger red (#f44336)

---

**Developed as a simple frontend demonstration project**
