from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from functools import wraps
from pathlib import Path
import sqlite3, random, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('NDA_SECRET_KEY', 'change-this-key-for-deployment')
BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / 'database.db'


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            score INTEGER NOT NULL, total INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('register', next=request.path))
        return view(*args, **kwargs)
    return wrapped


SUBJECTS = [
    {'name':'Mathematics','icon':'∑','desc':'Algebra, trigonometry, calculus, geometry and statistics.','url':'https://en.wikipedia.org/wiki/Mathematics','tag':'Paper I'},
    {'name':'English','icon':'文','desc':'Grammar, vocabulary, comprehension and usage.','url':'https://en.wikipedia.org/wiki/English_grammar','tag':'GAT'},
    {'name':'Physics','icon':'⚛','desc':'Mechanics, heat, light, sound, electricity and magnetism.','url':'https://en.wikipedia.org/wiki/Physics','tag':'GAT'},
    {'name':'Chemistry','icon':'⚗','desc':'Matter, elements, compounds, reactions and everyday chemistry.','url':'https://en.wikipedia.org/wiki/Chemistry','tag':'GAT'},
    {'name':'History','icon':'⌛','desc':'Indian history, freedom movement and world history basics.','url':'https://en.wikipedia.org/wiki/History_of_India','tag':'GAT'},
    {'name':'Geography','icon':'🌍','desc':'Physical, Indian and world geography.','url':'https://en.wikipedia.org/wiki/Geography_of_India','tag':'GAT'},
    {'name':'General Science','icon':'🔬','desc':'Biology, scientific developments and everyday science.','url':'https://en.wikipedia.org/wiki/Science','tag':'GAT'},
    {'name':'Current Affairs','icon':'📰','desc':'Follow national and international news and defence updates.','url':'https://www.pib.gov.in/','tag':'GAT'}
]

# Original NDA-pattern practice questions. Use official UPSC papers for authentic past papers.
QUESTION_BANK = [
('If 2x + 5 = 17, find x.', ['5','6','7','8'], '6', 'Algebra'),
('The sum of the first  n natural numbers is:', ['n²','n(n+1)/2','n(n−1)/2','2n'], 'n(n+1)/2', 'Algebra'),
(' sin 30° equals:', ['1','√3/2','1/2','0'], '1/2', 'Trigonometry'),
('The roots of x² − 5x + 6 = 0 are:', ['1, 6','−2, −3','2, 3','−1, −6'], '2, 3', 'Algebra'),
('The derivative of x³ with respect to x is:', ['x²','2x','3x²','3x'], '3x²', 'Calculus'),
('A fair coin is tossed once. Probability of getting heads is:', ['0','1/4','1/2','1'], '1/2', 'Probability'),
('The SI unit of force is:', ['Joule','Watt','Newton','Pascal'], 'Newton', 'Physics'),
('Which law explains action and reaction?', ['Newton’s first law','Newton’s second law','Newton’s third law','Law of gravitation'], 'Newton’s third law', 'Physics'),
('The speed of light in vacuum is approximately:', ['3 × 10⁶ m/s','3 × 10⁸ m/s','3 × 10¹⁰ m/s','300 m/s'], '3 × 10⁸ m/s', 'Physics'),
('Which instrument measures electric current?', ['Voltmeter','Ammeter','Barometer','Thermometer'], 'Ammeter', 'Physics'),
('The chemical symbol of sodium is:', ['So','S','Na','N'], 'Na', 'Chemistry'),
('A solution with pH 3 is:', ['Acidic','Neutral','Basic','Always salty'], 'Acidic', 'Chemistry'),
('Which gas is released during photosynthesis?', ['Nitrogen','Oxygen','Carbon dioxide','Hydrogen'], 'Oxygen', 'Biology'),
('The largest organ of the human body is:', ['Heart','Liver','Skin','Lung'], 'Skin', 'Biology'),
('The Revolt of 1857 began at:', ['Delhi','Meerut','Kanpur','Jhansi'], 'Meerut', 'History'),
('The Constitution of India was adopted on:', ['15 August 1947','26 January 1950','26 November 1949','2 October 1949'], '26 November 1949', 'Civics'),
('The Tropic of Cancer passes through how many Indian states?', ['6','7','8','9'], '8', 'Geography'),
('Which is the longest river in India by length within the country?', ['Yamuna','Ganga','Godavari','Narmada'], 'Ganga', 'Geography'),
('Choose the correctly spelled word:', ['Accomodation','Acommodation','Accommodation','Accommadation'], 'Accommodation', 'English'),
('Choose the synonym of “brave”.', ['Timid','Courageous','Careless','Weak'], 'Courageous', 'English'),
('Choose the antonym of “ancient”.', ['Old','Historic','Modern','Former'], 'Modern', 'English'),
('Select the correct sentence:', ['She go to school daily.','She goes to school daily.','She going school daily.','She gone to school daily.'], 'She goes to school daily.', 'English'),
('The headquarters of the United Nations is in:', ['Geneva','Paris','New York','London'], 'New York', 'General Knowledge'),
('The Indian Armed Forces are commanded constitutionally by the:', ['Prime Minister','President','Chief Justice','Home Minister'], 'President', 'Defence Awareness'),
('The Indian Naval Academy is located at:', ['Khadakwasla','Ezhimala','Dehradun','Dundigal'], 'Ezhimala', 'Defence Awareness'),
]


@app.route('/')
def home():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('register'))


@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not name or not email or len(password) < 8:
            error = 'Enter your name and email, and choose a password with at least 8 characters.'
        else:
            try:
                with get_db() as conn:
                    cur = conn.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)', (name,email,generate_password_hash(password)))
                    session['user_id'] = cur.lastrowid
                    session['user_name'] = name
                return redirect(url_for('dashboard'))
            except sqlite3.IntegrityError:
                error = 'This email is already registered. Please sign in.'
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session.clear(); session['user_id'] = user['id']; session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        error = 'Email or password is incorrect.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    with get_db() as conn:
        results = conn.execute('SELECT * FROM results WHERE user_id=? ORDER BY id DESC LIMIT 5',(session['user_id'],)).fetchall()
        stats = conn.execute('SELECT COUNT(*) AS tests, COALESCE(MAX(score),0) AS best FROM results WHERE user_id=?',(session['user_id'],)).fetchone()
    return render_template('dashboard.html', name=session.get('user_name','Cadet'), results=results, stats=stats)


@app.route('/subjects')
@login_required
def subjects(): return render_template('subjects.html', subjects=SUBJECTS)


@app.route('/quiz', methods=['GET','POST'])
@login_required
def quiz():
    if request.method == 'POST':
        questions = session.get('quiz_questions', [])
        score = sum(1 for i,q in enumerate(questions) if request.form.get(f'q{i}') == q['answer'])
        total = len(questions)
        with get_db() as conn:
            conn.execute('INSERT INTO results(user_id,score,total) VALUES(?,?,?)',(session['user_id'],score,total))
        session['score']=score; session['total']=total
        return redirect(url_for('result'))
    selected = random.sample(QUESTION_BANK, 10)
    session['quiz_questions'] = [{'question':q[0], 'options':q[1], 'answer':q[2], 'topic':q[3]} for q in selected]
    return render_template('quiz.html', questions=session['quiz_questions'])


@app.route('/result')
@login_required
def result():
    if 'score' not in session: return redirect(url_for('quiz'))
    return render_template('result.html', score=session.pop('score'), total=session.pop('total'))


@app.route('/podcasts')
@login_required
def podcasts():
    episodes = [
      {'title':'Discipline: the daily advantage','desc':'Build a consistent routine and protect your study hours.','image':'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80','url':'https://www.youtube.com/results?search_query=military+discipline+motivation'},
      {'title':'Stories of courage','desc':'Listen to stories of service, teamwork and resilience.','image':'https://images.unsplash.com/photo-1517976487492-5750f3195933?auto=format&fit=crop&w=900&q=80','url':'https://www.youtube.com/results?search_query=Indian+Army+bravery+stories'},
      {'title':'Focus under pressure','desc':'Practical ideas for staying calm during preparation and exams.','image':'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=900&q=80','url':'https://www.youtube.com/results?search_query=focus+study+motivation'}]
    return render_template('podcasts.html', episodes=episodes)


# ----------------- GOOGLE SEARCH CONSOLE VERIFICATION -----------------

@app.route('/google82d783a71581b1df.html')
def google_verification():
    return send_from_directory(BASE_DIR, 'google82d783a71581b1df.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)