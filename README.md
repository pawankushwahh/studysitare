# StudySitare Learning Management System

A modern learning management system built for Sitare University students to access course materials, track progress, and interact with mentors.

## Features

- **User Management**
  - Separate login portals for students and administrators
  - Secure authentication with password hashing
  - Profile management with customizable settings

- **Course Management**
  - Semester-wise subject organization
  - Progress tracking for each subject
  - Resource management for study materials

- **Interactive Dashboard**
  - Student progress visualization
  - Subject overview and quick access
  - Mentor communication system

- **Responsive Design**
  - Modern, clean interface
  - Mobile-friendly layout
  - Smooth animations and transitions

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/studysitare.git
   cd studysitare
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file with the following configuration:
   ```
   SECRET_KEY=your-secret-key-here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-specific-password
   ```

5. Initialize the database:
   ```bash
   python app.py
   ```

6. Run the application:
   ```bash
   flask run
   ```

## Technologies Used

- **Backend**
  - Flask (Python web framework)
  - SQLAlchemy (Database ORM)
  - Flask-Login (User authentication)
  - Flask-Mail (Email notifications)

- **Frontend**
  - Bootstrap 5 (UI framework)
  - Font Awesome (Icons)
  - Custom CSS animations
  - AJAX for form handling

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
