# Student Course Feedback Management System

## Overview

A full-stack web application for managing student course feedback. The system provides a complete authentication flow and feedback management interface with Flask backend, PostgreSQL database, and vanilla JavaScript frontend. All data is securely stored in the database with user isolation, and passwords are hashed for security.

## Recent Changes

**November 15, 2025**: Backend and database integration completed
- Migrated from localStorage-only frontend to full-stack architecture
- Created Flask backend with REST API endpoints
- Integrated PostgreSQL database for persistent storage
- Implemented secure password hashing using werkzeug
- Added user authentication with session management
- Implemented user-specific feedback isolation (each user sees only their own feedback)
- Added server-side input validation and error handling
- Organized files into proper structure (app.py and static/ folder)
- Updated all frontend JavaScript to communicate with backend API
- Created comprehensive database schema with users and feedback tables
- Fixed all LSP errors and security vulnerabilities

**Earlier (November 15, 2025)**: Initial frontend implementation
- Created login page with email/password form
- Built main feedback page with course name, rating (1-5), and comments fields
- Implemented feedback display with clean card-based layout
- Created modern, minimalistic UI with purple gradient theme
- Made the design fully responsive for mobile and desktop

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Full-Stack Architecture

**Technology Stack**: Flask (Python backend), PostgreSQL database, and vanilla JavaScript frontend with no frameworks.

**Rationale**: Provides a real-world full-stack application with proper authentication, database persistence, and RESTful API design while maintaining simplicity on the frontend.

**File Structure**:
- `app.py`: Flask backend server with API endpoints and database logic
- `static/login.html`: Login/registration page
- `static/index.html`: Main feedback submission and display page
- `static/styles.css`: All styling with modern, minimalistic design
- `static/app.js`: Frontend JavaScript for API communication
- `static/README.md`: Project documentation

### Backend Architecture

**Flask Framework**: Lightweight Python web framework for building the REST API.

**API Endpoints**:
- `POST /api/login` - Authenticate existing users or register new users with password hashing
- `POST /api/logout` - Clear user session and log out
- `GET /api/check-auth` - Verify if user is authenticated (for route protection)
- `GET /api/feedback` - Retrieve all feedback for the logged-in user
- `POST /api/feedback` - Submit new feedback entry
- `DELETE /api/feedback/clear` - Delete all feedback for the logged-in user

**Session Management**: Uses Flask sessions with secure cookies to maintain authentication state across requests.

**CORS Support**: Flask-CORS enabled to support frontend-backend communication with credentials.

**Pros**:
- Real database persistence
- Secure authentication with password hashing
- User data isolation
- Scalable architecture
- RESTful API design

### Database Architecture

**PostgreSQL Database**: Using Replit's built-in PostgreSQL (Neon-backed) for data storage.

**Schema Design**:

**Users Table**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Feedback Table**:
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

**Rationale**: 
- Normalized schema with foreign key relationships
- User-specific feedback isolation via user_id foreign key
- Database constraints for data integrity (rating must be 1-5)
- Timestamps for auditing

**Pros**:
- Persistent storage across sessions and devices
- Multi-user support with data isolation
- Relational data model for complex queries
- Backup and recovery capabilities
- No storage size limitations like localStorage

### Authentication & Security

**Password Hashing**: Uses `werkzeug.security` (included with Flask) to:
- Hash passwords with `generate_password_hash()` before storing
- Verify passwords with `check_password_hash()` during login
- Never store plain-text passwords

**Auto-Registration**: If a user doesn't exist, the system automatically creates an account with the provided email and password.

**Password Validation**: Existing users must provide the correct password to log in (returns 401 if incorrect).

**Session-Based Auth**: Flask sessions store user_id and email after successful authentication.

**Route Protection**: All API endpoints (except login and check-auth) require authentication and return 401 if not logged in.

**Input Validation**: Server-side validation for:
- Required fields (email, password, course name, rating, comments)
- Rating range (1-5)
- JSON payload validation to prevent None-subscript errors

**XSS Prevention**: HTML escaping in frontend JavaScript for user-generated content.

**User Isolation**: Database queries filter by user_id to ensure users only see their own data.

### Frontend Architecture

**Vanilla JavaScript with Fetch API**: All API communication uses modern fetch() with credentials.

**Async/Await Pattern**: Clean asynchronous code for API calls with try/catch error handling.

**No External Dependencies**: Pure HTML5, CSS3, and ES6+ JavaScript.

**Features**:
- Authentication check on page load with auto-redirect
- Dynamic feedback rendering from database
- Form validation before submission
- Success/error notifications
- Responsive design

### UI/UX Features

**Design System**:
- Color Palette: Purple-blue gradient (#667eea to #764ba2)
- Soft shadows for depth
- Rounded corners (8-12px border radius)
- Smooth transitions and hover effects
- Modern button styles with transform effects

**Interactive Elements**:
- Success/error notifications with slide-in animations
- Hover effects on buttons and feedback cards
- Confirmation dialog for destructive actions (clear all)
- Empty state messaging when no feedback exists
- Form reset after successful submission
- Loading states during API calls

**Responsive Design**: 
- Mobile-first approach
- Flexible layouts that adapt to screen size
- Touch-friendly button sizes
- Readable text across all devices

## External Dependencies

**Backend**:
- `flask` - Web framework
- `flask-cors` - CORS support
- `psycopg2-binary` - PostgreSQL database adapter
- `werkzeug` - Password hashing (included with Flask)

**Frontend**: 
- None - Pure vanilla JavaScript

## Development Server

**Current Setup**: Flask development server on port 5000

**Command**: `python app.py`

**Workflow**: Configured to run Flask backend with webview output

**Database**: PostgreSQL database automatically initialized on server start with environment variables:
- `DATABASE_URL` - Connection string
- `SESSION_SECRET` - Flask session secret
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - Individual connection params

## Deployment Considerations

1. **Production WSGI Server**: Replace Flask dev server with Gunicorn or uWSGI
2. **Environment Variables**: Ensure SESSION_SECRET is set to a strong random value
3. **Database Migrations**: Current schema is managed via CREATE TABLE IF NOT EXISTS
4. **HTTPS**: Required for secure session cookies in production
5. **Password Requirements**: Consider adding password strength requirements

## Potential Improvements

1. **Password Requirements**: Add minimum length, complexity validation
2. **Email Verification**: Send verification email on registration
3. **Password Reset**: Add forgot password functionality
4. **Feedback Editing**: Allow users to edit individual feedback entries
5. **Feedback Deletion**: Delete individual feedback (not just clear all)
6. **Sorting/Filtering**: Add UI controls to sort/filter feedback
7. **Data Export**: Download feedback as JSON or CSV
8. **Star Rating UI**: Replace dropdown with interactive star component
9. **Search**: Add search functionality across feedback
10. **Pagination**: Limit displayed feedback and paginate results
11. **Profile Management**: Allow users to update email or password
12. **Rate Limiting**: Prevent brute force login attempts
13. **CSRF Protection**: Add CSRF tokens to forms
