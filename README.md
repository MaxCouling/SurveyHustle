# SurveyHustle
SurveyHustle, a group project developed in INFOMGMT 399

<h2>Installation</h2>

<p>Follow these steps to set up the project on your local machine:</p>

<h3>Prerequisites</h3>

<ul>
  <li><strong>Python 3.10 or 3.11 (Python 3.12 may have some compatibility issues)</strong></li>
  <li><strong>Git</strong> (for cloning the repository)</li>
  <li>
    <strong>Virtual Environment Tool</strong> (optional but recommended, e.g., <code>venv</code> or <code>conda</code>)
  </li>
</ul>

<h3>Steps</h3>

<ol>
  <li>
    <strong>Clone the Repository</strong>
    <p>Clone the project repository to your local machine using Git:</p>
    <pre><code class="bash">git clone https://github.com/MaxCouling/SurveyHustle
cd SurveyHustle
</code></pre>
  </li>

  <li>
    <strong>Create a Virtual Environment</strong>
    <p>It's recommended to use a virtual environment to manage project dependencies without affecting your global Python installation.</p>
    <pre><code class="bash">python -m venv venv
</code></pre>
  </li>

  <li>
    <strong>Activate the Virtual Environment</strong>
    <p>On Windows:</p>
    <pre><code class="bash">venv\Scripts\activate
</code></pre>
    <p>On macOS/Linux:</p>
    <pre><code class="bash">source venv/bin/activate
</code></pre>
  </li>

  <li>
    <strong>Install Dependencies</strong>
    <p>Install all the required Python packages using pip:</p>
    <pre><code class="bash">pip install -r requirements.txt
</code></pre>
  </li>

  <li>
    <strong>Initialize the Database</strong>
    <p>During development, each developer will have their own local database. You'll need to create and initialise it before running the application.</p>
    <p><strong>Create the Database Tables</strong></p>
    <pre><code class="bash">flask shell
</code></pre>
    <p>Inside the Flask shell:</p>
    <pre><code class="python">from app import db
db.create_all()
exit()
</code></pre>
    <p>This will create the necessary tables in your local <code>app.db</code> SQLite database.</p>
  </li>

  <li>
    <strong>Run the Application</strong>
    <p>Start the Flask development server:</p>
    <pre><code class="bash">flask run
</code></pre>
    <p>The application will be accessible at <a href="http://localhost:5000">http://localhost:5000</a>.</p>
  </li>

  <li>
    <strong>Access the Application</strong>
    <p>Open your web browser and navigate to <a href="http://localhost:5000">http://localhost:5000</a>.<br>
    You can now register a new account and start using SurveyHustle locally.</p>
  </li>
</ol>
