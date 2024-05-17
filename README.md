# README

## Overview

This project is a web application for annotating blog comments with various labels for analysis. It was used to create the Icelandic "Ice and Fire" dataset (https://huggingface.co/datasets/hafsteinn/ice_and_fire). It consists of a Flask-based backend and a React frontend. The application allows users to register, log in, and annotate comments with specific labels based on the selected task.

## Structure

The project is divided into two main directories:
- `backend`: Contains the Flask application and related configurations.
- `frontend`: Contains the React application.

## Backend

### Setup

1. **Install Dependencies**:
   Ensure you have Python installed. Navigate to the `backend` directory and run:
   ```sh
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Set up the environment variables. Create a `.env` file and specify the following variables:
   ```sh
   FLASK_ENV=development
   DATABASE_URL=sqlite:///annotations.db  # Or your database URL
   ```

3. **Database Initialization**:
   Initialize the database by running:
   ```sh
   flask db init
   flask db migrate
   flask db upgrade
   ```

4. **Run the Server**:
   Start the Flask server:
   ```sh
   flask run
   ```
*Note that there is no data provided to annotate so the project might not build properly unless you fill the database with your data first.*

### Deployment

To deploy the backend, ensure you have a web server setup. The `Procfile` for deployment using Gunicorn is provided:
```sh
web: gunicorn app:app --preload
```

### Files

- **`requirements.txt`**: Lists all the dependencies required for the backend.
- **`Procfile`**: Specifies the command to run the application using Gunicorn.
- **`app.py`**: The main Flask application file containing routes, models, and logic.

### Key Features

- **User Authentication**: Registration and login functionalities using Flask-Login.
- **Database Models**: Defined using SQLAlchemy for BlogPost, Comment, Annotator, and Annotation.
- **Annotation Routes**: API endpoints for registering, logging in, logging out, fetching comments, and submitting annotations.
- **CORS and Sessions**: Handled using Flask-CORS and Flask-Session for secure cross-origin requests and session management.

## Frontend

### Setup

1. **Install Dependencies**:
   Ensure you have Node.js installed. Navigate to the `frontend` directory and run:
   ```sh
   npm install
   ```

2. **Run the Development Server**:
   Start the React development server:
   ```sh
   npm start
   ```

### Proxy Setup

The `frontend/src/setupProxy.js` file sets up a proxy to forward API requests to the backend server during development (we recommend to build the front-end project (`npm build`) and serve it through python in production):
```js
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  const proxyConfig = createProxyMiddleware({
    target: 'https://localhost:5000',
    changeOrigin: true,
    secure: false,
  });

  ['/login', '/annotate', '/register', '/logout', '/cleanup_test_data', '/leaderboard', '/is_logged_in', '/user_task_counts'].forEach(path => {
    app.use(path, proxyConfig);
  });
};
```

### Files

- **`App.js`**: The main React component containing the application logic.
- **`App.css`**: Styling for the React application.
- **`setupProxy.js`**: Proxy configuration for API requests.
- **`index.js`**: Entry point for the React application.
- **`components`**: Directory containing reusable React components like `TaskInstructions` and `UserStatus`.

### Key Features

- **Task Selection**: Users can select tasks to annotate comments.
- **Label Selection**: Interactive buttons for selecting labels based on the chosen task.
- **Login and Registration**: Forms for user authentication.
- **Comment Navigation**: Buttons for navigating between comments.
- **Instructions and Status**: Components to display task instructions and user annotation status.

## Running Tests

To run the frontend tests, navigate to the `frontend` directory and run:
```sh
npm test
```

## Instructions

Instructions for each task are stored as markdown files in `frontend/public/instructions/`. These instructions are fetched and displayed in the application as needed. Note that these instructions are in Icelandic and you may need to adapt them for your tasks.

## Contributions

To contribute to this project, fork the repository, create a new branch for your feature or bugfix, and submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
