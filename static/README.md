# Student Course Feedback Management System

A full-stack web application for managing student course feedback with a Flask backend, PostgreSQL database, and vanilla JavaScript frontend.

## Features

- **User Authentication**: Secure login with password hashing (using werkzeug)
- **Feedback Submission**: Submit feedback with course name, rating (1-5), and comments
- **Feedback Display**: View all your submitted feedback in a clean, organized list
- **Database Storage**: All data is stored in a PostgreSQL database
- **User Isolation**: Each user only sees their own feedback
- **Clear Feedback**: Remove all your feedback with a single click
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Clean, minimalistic design with smooth animations and hover effects

## Tech Stack

### Backend
- **Flask**: Python web framework
- **PostgreSQL**: Relational database for data persistence
- **werkzeug.security**: Password hashing and validation
- **Flask-CORS**: Cross-origin resource sharing support
- **psycopg2**: PostgreSQL database adapter

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **Vanilla JavaScript**: ES6+ with fetch API for backend communication
- **No frameworks**: Pure frontend code for simplicity

## File Structure

```
/
├── app.py                # Flask backend server
├── static/               # Frontend files
│   ├── login.html        # Login page
│   ├── index.html        # Main feedback page
│   ├── styles.css        # All styling
│   ├── app.js            # Frontend JavaScript
│   └── README.md         # This file
```

## How to Use

1. **Login/Register**: 
   - Open the application in your browser
   - Enter your email and password
   - If it's your first time, an account will be created automatically
   - Existing users: password will be validated

2. **Submit Feedback**:
   - Fill in the course name
   - Select a rating (1-5)
   - Write your comments
   - Click "Submit Feedback"

3. **View Feedback**:
   - All your submitted feedback appears below the form
   - Newest feedback appears first
   - Only you can see your feedback

4. **Clear Feedback**:
   - Click "Clear All Feedback" to remove all your entries
   - Confirm the action in the popup

5. **Logout**:
   - Click the "Logout" button to end your session

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Feedback Table
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    course_name VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

- `POST /api/login` - Authenticate or register a user
- `POST /api/logout` - End user session
- `GET /api/check-auth` - Check authentication status
- `GET /api/feedback` - Get all feedback for the current user
- `POST /api/feedback` - Submit new feedback
- `DELETE /api/feedback/clear` - Delete all feedback for the current user

## Security Features

- **Password Hashing**: Passwords are hashed using werkzeug's secure hashing
- **Session Management**: Flask sessions with secure cookies
- **Input Validation**: Server-side validation for all inputs
- **XSS Protection**: HTML escaping for user-generated content
- **User Isolation**: Users can only access their own feedback

## Running the Application

The application runs on port 5000 using Flask's development server:

```bash
python app.py
```

Then open your browser to the provided URL.

## Environment Variables

The application uses these environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Secret key for Flask sessions

## Browser Compatibility

Works in all modern browsers that support:
- HTML5
- CSS3
- ES6+ JavaScript
- Fetch API

## Notes

- Each user's feedback is isolated - you only see your own entries
- Passwords are securely hashed and never stored in plain text
- The application uses Flask sessions for authentication
- All database operations are server-side for security

## Color Palette

- Primary Gradient: Purple to Blue (#667eea to #764ba2)
- Background: Light gray (#f9f9f9)
- Text: Dark gray (#333)
- Success: Green (#4caf50)
- Error/Danger: Red (#f44336)

---

**A simple yet powerful full-stack feedback management system**
