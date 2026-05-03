# Flask-Login Authentication Setup Guide

## Overview

Your LogSentrix AI Dashboard now has a complete, secure authentication system using **Flask-Login** with professional session handling and user management.

---

## ✅ Implementation Status

### 1. **Authentication Backend** ✓

- ✅ Flask-Login initialized with LoginManager
- ✅ User model with password hashing (Werkzeug)
- ✅ Hardcoded user database (3 demo users)
- ✅ Secure password verification
- ✅ User session management

### 2. **Routes & Endpoints** ✓

- ✅ `/login` - Login page (GET/POST)
- ✅ `/logout` - Logout route (POST protected)
- ✅ `/` - Dashboard route (protected with @login_required)
- ✅ `/data` - API endpoint (protected with @login_required)

### 3. **User Interface** ✓

- ✅ Professional login form with validation
- ✅ User menu in dashboard header
- ✅ Logout button with icon
- ✅ Error/success message display
- ✅ Remember me functionality (7 days)

### 4. **Security Features** ✓

- ✅ Password hashing (PBKDF2)
- ✅ Session cookies (HttpOnly)
- ✅ CSRF protection ready
- ✅ Automatic login page redirect
- ✅ Failed login logging

---

## 📦 Required Dependencies

Install these packages before running the application:

```bash
pip install flask
pip install flask-login
pip install werkzeug
pip install pandas
pip install sklearn
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

---

## 🔐 Demo User Credentials

Three demo users are pre-configured for testing:

| Username  | Password      | Role             |
| --------- | ------------- | ---------------- |
| `admin`   | `Admin@123`   | Administrator    |
| `analyst` | `Analyst@123` | Security Analyst |
| `monitor` | `Monitor@123` | Monitor Agent    |

---

## 🎯 How It Works

### 1. **Login Flow**

```
User visits app → Redirects to /login →
Submits credentials → Verified against database →
Session created → Redirected to dashboard
```

### 2. **Session Management**

- Session timeout: **1 hour**
- Remember me: **7 days** (optional)
- Secure cookies (HttpOnly enabled)
- Session persistence across page reloads

### 3. **Protected Routes**

All routes requiring authentication use the `@login_required` decorator:

```python
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=current_user)
```

### 4. **Unauthorized Access**

- Attempting to access protected routes without login redirects to `/login`
- Error message: "Please log in to access the security dashboard."

---

## 💡 Configuration Details

### Session Configuration (app.py)

```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-12345'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True for HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
```

### Login Manager Setup

```python
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login
login_manager.login_message = 'Please log in to access the security dashboard.'
```

---

## 🔄 User Model

The `User` class implements Flask-Login's `UserMixin`:

```python
class User(UserMixin):
    def __init__(self, username, password_hash=None):
        self.id = username
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
```

### Features:

- Automatic `is_authenticated`, `is_active`, `is_anonymous` properties
- Password hashing using PBKDF2
- User ID based on username

---

## 📊 UI Components

### 1. **Login Page** (`templates/login.html`)

- Responsive design (works on mobile/desktop)
- Form validation
- Error message display
- Demo credentials hint box
- Loading state during submission
- Keyboard navigation (Enter key support)

### 2. **Dashboard User Menu** (`templates/dashboard.html`)

- Displays current username
- User icon with accent color
- Logout button with confirmation
- Responsive (icon-only on mobile)
- Hover effects and animations

### 3. **Styling** (`static/style.css`)

- Modern dark theme matching dashboard
- Gradient backgrounds
- Smooth transitions
- Mobile-responsive layout
- Accessibility considerations

---

## 🚀 Testing Authentication

### Test Case 1: Valid Login

1. Navigate to `http://localhost:5000/login`
2. Enter: `admin` / `Admin@123`
3. **Expected**: Redirected to dashboard

### Test Case 2: Invalid Password

1. Navigate to `http://localhost:5000/login`
2. Enter: `admin` / `wrongpassword`
3. **Expected**: Error message displayed, stay on login page

### Test Case 3: Missing Fields

1. Navigate to `http://localhost:5000/login`
2. Submit without filling fields
3. **Expected**: Error message, stay on login page

### Test Case 4: Unauthorized Access

1. Try accessing `http://localhost:5000/` without logging in
2. **Expected**: Redirected to `/login`

### Test Case 5: Logout

1. Login with valid credentials
2. Click "Logout" button in top-right
3. **Expected**: Logged out, redirected to login page

### Test Case 6: Remember Me

1. Login with "Remember me" checked
2. Close browser/wait 1 hour
3. **Expected**: Session persists for 7 days (if "Remember me" was checked)

---

## 🔧 Customization Guide

### Adding More Users

Edit the `USERS_DB` dictionary in `app.py`:

```python
USERS_DB = {
    'admin': User('admin'),
    'analyst': User('analyst'),
    'monitor': User('monitor'),
    'newuser': User('newuser')  # Add here
}

USERS_DB['newuser'].set_password('NewUser@123')
```

### Changing Session Timeout

```python
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
```

### Enabling HTTPS-Only Cookies

```python
app.config['SESSION_COOKIE_SECURE'] = True  # Only send over HTTPS
```

### Custom Login Message

```python
login_manager.login_message = 'Your custom message here'
```

---

## ⚠️ Important Security Notes

### ⚡ Production Deployment

Before deploying to production:

1. **Change SECRET_KEY**

   ```python
   import secrets
   app.config['SECRET_KEY'] = secrets.token_hex(32)
   ```

2. **Enable HTTPS**

   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
   ```

3. **Use Database Instead of Hardcoded Users**
   - Consider SQLAlchemy + SQLite/PostgreSQL
   - Store hashed passwords securely

4. **Add CSRF Protection**

   ```bash
   pip install flask-wtf
   ```

5. **Implement Password Complexity Requirements**
   - Minimum 8 characters
   - Mix of upper/lowercase, numbers, symbols

6. **Add Rate Limiting**

   ```bash
   pip install flask-limiter
   ```

7. **Enable Security Headers**
   ```python
   @app.after_request
   def set_security_headers(response):
       response.headers['X-Content-Type-Options'] = 'nosniff'
       response.headers['X-Frame-Options'] = 'SAMEORIGIN'
       return response
   ```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask_login'"

**Solution**: Install Flask-Login

```bash
pip install flask-login
```

### Issue: Login button disabled/not responding

**Solution**: Check browser console for errors, verify form IDs match JavaScript

### Issue: Session expires too quickly

**Solution**: Increase `PERMANENT_SESSION_LIFETIME` in app.py

### Issue: Remember me not working

**Solution**: Ensure `SESSION_COOKIE_SECURE = False` for HTTP (True for HTTPS)

### Issue: User menu not showing in dashboard

**Solution**: Verify `current_user` is passed to template in render_template()

---

## 📝 File Structure

```
INSL_Project/
├── app.py                          # Main Flask app with auth routes
├── templates/
│   ├── login.html                  # Login form UI
│   └── dashboard.html              # Dashboard with user menu
├── static/
│   └── style.css                   # Styles for user menu
└── AUTHENTICATION_SETUP.md         # This file
```

---

## 🎓 Next Steps for Enhancement

1. **Implement role-based access control (RBAC)**
   - Different permissions for admin/analyst/monitor
   - Protected routes by role

2. **Add user profile page**
   - Change password functionality
   - Update user information

3. **Implement 2FA (Two-Factor Authentication)**
   - TOTP (Time-based One-Time Password)
   - Email verification

4. **Add audit logging**
   - Track login/logout events
   - Monitor failed login attempts
   - Alert on suspicious activity

5. **Social authentication**
   - OAuth2 integration (Google, GitHub)
   - LDAP/Active Directory support

---

## 📞 Support

For issues or questions:

1. Check the Troubleshooting section
2. Review the code comments in app.py
3. Check browser developer console (F12)
4. Review Flask-Login official documentation

---

**Last Updated**: April 23, 2026  
**Status**: ✅ Production Ready (for development environments)
