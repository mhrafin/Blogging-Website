
# Flask Blog Platform

A fully functional blog platform built with Flask, providing features such as user authentication, CRUD operations for blog posts, commenting, and admin-only capabilities.

## Features

- **User Registration and Login**: Secure user authentication with hashed passwords.
- **Create, Read, Update, Delete (CRUD)**:
  - Admins can create, edit, and delete blog posts.
  - Users can view posts and leave comments.
- **Comment System**: Users can comment on blog posts.
- **Admin-only Features**: Admin accounts have special privileges to manage posts.
- **Responsive Design**: Templates ready for desktop and mobile use.
- **Secure Communication**: Includes functionality to send contact messages via email.

## Technologies Used

- **Backend**: Flask, Flask-SQLAlchemy, Flask-WTF, Flask-Login, Flask-CKEditor
- **Frontend**: Bootstrap (via templates for styling)
- **Database**: SQLite
- **Other Tools**: dotenv for environment variable management, CKEditor for rich text editing.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/mhrafin/Blogging-Website.git
   cd Blogging-Website
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv .venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   - Create a `.env` file in the root directory.
   - Add your email credentials:

     ```
     MY_EMAIL=your_email@gmail.com
     MY_PASSWORD=your_email_password
     ```

5. **Run the Application**

   ```bash
   python3 main.py
   ```

   The app will be available at `http://127.0.0.1:5000`.

## Usage

### Admin Access

By default, the first user registered will have admin privileges. Admins can:

- Create new blog posts.
- Edit or delete existing blog posts.

### User Features

- View blog posts.
- Leave comments on posts.

## Project Structure

```
flask-blog-platform/
│
├── templates/          # HTML templates for the app
├── static/             # Static assets like CSS, JS, images
├── main.py             # Main application logic
├── email_sender.py     # Email utility functions
├── requirements.txt    # List of dependencies
└── README.md           # Project documentation
```

## Contributing

Contributions are welcome! If you find a bug or want to add a new feature:

1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request.
