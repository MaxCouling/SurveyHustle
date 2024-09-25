# SurveyHustle SurveyHustle
a group project developed in INFOMGMT 399

Installation
------------

Follow these steps to set up the project on your local machine:

### Prerequisites

*   **Python 3.10 or 3.11 (Python 3.12 may have some compatibility issues)**
*   **Git** (for cloning the repository)
*   **Virtual Environment Tool** (optional but recommended, e.g., `venv` or `conda`)
*   **Node.js and npm** (for Tailwind CSS and DaisyUI)

### Steps

1.  **Clone the Repository**
    
    Clone the project repository to your local machine using Git:
    
        git clone https://github.com/MaxCouling/SurveyHustle
        cd SurveyHustle
        
    
2.  **Create a Virtual Environment**
    
    It's recommended to use a virtual environment to manage project dependencies without affecting your global Python installation.
    
        python -m venv venv
        
    
3.  **Activate the Virtual Environment**
    
    On Windows:
    
        venv\Scripts\activate
        
    
    On macOS/Linux:
    
        source venv/bin/activate
        
    
4.  **Install Dependencies**
    
    Install all the required Python packages using pip:
    
        pip install -r requirements.txt
        
    
5.  **Initialize the Database**
    
    During development, each developer will have their own local database. You'll need to create and initialise it before running the application. It is a very, very good idea when running locally to delete your database and start a new one when pulling new changes, as database schema is subject to change.
    
    **Create the Database Tables**
    
        flask shell
        
    
    Inside the Flask shell:
    
        from app import db
        db.create_all()
        exit()
        
    
    This will create the necessary tables in your local `app.db` SQLite database.
    
6.  **Run the Application**
    
    Start the Flask development server:
    
        flask run
        
    
    The application will be accessible at [http://localhost:5000](http://localhost:5000).
    

Sure! Below is the Markdown version of your instructions, formatted with appropriate headings, subheadings, and code blocks for better readability and structure.

---

# Set Up Tailwind CSS and DaisyUI

Tailwind CSS and DaisyUI are used for styling the application. Follow these steps to set them up:

## 6.1 Install Node.js and npm

Tailwind CSS and DaisyUI require Node.js and npm. If you don't have them installed, download and install them from the [Node.js website](https://nodejs.org/).

## 6.2 Initialize npm

Initialize npm in your project directory:

```bash
npm init -y
```

This command creates a `package.json` file with default settings.

## 6.3 Install Tailwind CSS and DaisyUI

Install Tailwind CSS and DaisyUI via npm:

```bash
npm install tailwindcss daisyui
```

## 6.4 Initialize Tailwind CSS Configuration

Generate the `tailwind.config.js` file:

```bash
npx tailwindcss init
```

This command creates a `tailwind.config.js` file in your project directory.

## 6.5 Configure `tailwind.config.js`

Update `tailwind.config.js` to include DaisyUI and specify the content paths:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/templates/**/*.html', // Adjust the path to your templates
    './app/static/**/*.js',      // If you have custom JS files
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      "light",
      "dark",
      "cupcake",
      "bumblebee",
      "emerald",
      "corporate",
      "synthwave",
      "retro",
      "cyberpunk",
      "valentine",
      "halloween",
      "garden",
      "forest",
      "aqua",
      "lofi",
      "pastel",
      "fantasy",
      "wireframe",
      "black",
      "luxury",
      "dracula",
      "cmyk",
      "autumn",
      "business",
      "acid",
      "lemonade",
      "night",
      "coffee",
      "winter",
    ],
  },
}
```

**Explanation:**

- **Content Paths:** Ensure Tailwind scans all your HTML and JS files to include the necessary styles.
- **DaisyUI Plugin:** Adds DaisyUI as a plugin.
- **Themes:** Lists all the DaisyUI themes you want to use.

## 6.6 Create Tailwind Input CSS File

Create a CSS file where Tailwind CSS directives will be added. For example, create `app/static/css/tailwind.css` with the following content:

```css
/* app/static/css/tailwind.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles can go here */
```

## 6.7 Build Tailwind CSS

Add a build script to your `package.json`:

```json
// package.json
{
  // ... existing content ...
  "scripts": {
    "build:css": "npx tailwindcss -i ./app/static/css/tailwind.css -o ./app/static/css/output.css --watch"
  },
  // ... existing content ...
}
```


7.  **Access the Application**
    
    Open your web browser and navigate to [http://localhost:5000](http://localhost:5000).  
    You can now register a new account and start using SurveyHustle locally.
