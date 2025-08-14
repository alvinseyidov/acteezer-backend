# Acteezer - Activity Social Platform

Modern, beautiful social platform for connecting people through activities, built with Django and designed with travel website aesthetics.

## Features

### 🌟 Modern Travel Website Design
- Beautiful, responsive UI inspired by modern travel platforms
- Gradient backgrounds and smooth animations
- Clean, professional layout with excellent UX

### 📱 Multi-Step Registration
1. **Phone verification** - SMS OTP system
2. **Personal details** - Name collection
3. **Languages** - Multi-language selection
4. **Birthday** - Age verification
5. **Photo upload** - Minimum 2 photos required
6. **Bio** - Personal description
7. **Interests** - Activity preferences
8. **Location** - City and map pin selection

### 🌍 Azerbaijani Language Support
- Full localization in Azerbaijani
- Cultural relevance for local users
- Appropriate regional language options

### 🔐 Security Features
- Phone-based authentication
- OTP verification system
- Custom user manager
- Secure password handling

## Project Structure

```
backend/
├── config/                 # Django project settings
├── accounts/              # User management app
│   ├── models.py         # User, Language, Interest models
│   ├── views.py          # Registration flow views
│   ├── admin.py          # Admin interface
│   └── management/       # Custom commands
├── templates/            # HTML templates
│   └── accounts/        # Registration templates
├── static/              # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
└── media/               # User uploads
```

## Key Models

### User Model
- Phone-based authentication (no username)
- Step-by-step registration tracking
- Profile completion validation
- Location data (city, coordinates)
- Multi-language and interest support

### Supporting Models
- **Language**: Available languages for users
- **Interest**: Activity categories and preferences
- **UserImage**: Profile photos (minimum 2 required)
- **OTPVerification**: SMS verification tracking

## Technology Stack

- **Backend**: Django 5.2.5 + Django REST Framework
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5.3 + Custom CSS
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Poppins)

## Setup Instructions

1. **Activate virtual environment**:
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Setup initial data**:
   ```bash
   python manage.py setup_initial_data
   ```

5. **Start development server**:
   ```bash
   python manage.py runserver
   ```

## Registration Flow

Users complete registration in logical steps:

1. **Phone** → OTP verification
2. **Name** → First and last name
3. **Languages** → Multi-select from available options
4. **Birthday** → Age validation (16-100)
5. **Photos** → Upload 2+ profile images
6. **Bio** → Personal description (50+ characters)
7. **Interests** → Activity preferences
8. **Location** → City selection with map coordinates

Each step validates data before proceeding to the next, ensuring complete and accurate user profiles.

## Design Features

### Modern Travel Aesthetic
- Gradient hero sections with wave patterns
- Card-based layouts with subtle shadows
- Smooth hover animations and transitions
- Professional color scheme (blues, whites, accent colors)

### Mobile-First Responsive
- Bootstrap 5 grid system
- Custom breakpoints for optimal viewing
- Touch-friendly interface elements
- Progressive enhancement

### Azerbaijani Localization
- Complete UI translation
- Cultural considerations for local market
- Regional language support in selection

## Admin Interface

Comprehensive admin panel with:
- User management with registration progress tracking
- Language and interest category management
- Photo preview and management
- OTP verification monitoring
- Advanced filtering and search capabilities

## Next Steps

The foundation is complete for:
- Activity creation and management
- User matching and recommendations
- Real-time messaging
- Event planning and coordination
- Payment integration
- Mobile app API endpoints

This platform provides a solid foundation for building a comprehensive social activity platform with modern design and excellent user experience.

