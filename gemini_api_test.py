
from flask import Flask, request, jsonify, render_template_string
from google import genai
import re
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/Users/pro/Desktop/GitHub Repos/IntelliFit/Planning/.env")

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntelliFit Workout Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
            min-height: 100vh;
        }
        .container { max-width: 950px; margin-top: 40px; }
        .card {
            margin-bottom: 24px;
            border-radius: 18px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            border: none;
        }
        .json-section {
            background: linear-gradient(120deg, #f8f9fa 60%, #e0eafc 100%);
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
            animation: fadeIn 0.7s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .section-title {
            font-weight: 700;
            margin-top: 32px;
            margin-bottom: 16px;
            color: #0077b6;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .output-label { font-weight: 600; color: #495057; }
        .output-value { color: #212529; }
        .tips-list, .equipment-list { padding-left: 20px; }
        .motivation {
            font-style: italic;
            color: #0077b6;
            margin-top: 24px;
            font-size: 1.2em;
            background: #e0eafc;
            border-radius: 8px;
            padding: 12px 18px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }
        .json-raw {
            font-size: 0.95em;
            background: #f1f3f4;
            border-radius: 6px;
            padding: 12px;
            margin-top: 16px;
        }
        .icon {
            font-size: 1.3em;
            color: #00b4d8;
            margin-right: 6px;
        }
        .form-title {
            font-size: 1.5em;
            font-weight: 700;
            color: #0077b6;
            margin-bottom: 18px;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%);
            border: none;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        }
        .btn-primary:hover {
            background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
        }
        .spinner-border { color: #00b4d8; }
    </style>
</head>
<body>
    <div id="loadingScreen" style="position:fixed;top:0;left:0;width:100vw;height:100vh;background:linear-gradient(135deg,#e0eafc 0%,#cfdef3 100%);z-index:9999;display:none;align-items:center;justify-content:center;flex-direction:column;">
        <div class="text-center">
            <span class="spinner-border" style="width:4rem;height:4rem;"></span>
            <div style="font-size:1.3em;color:#0077b6;margin-top:18px;font-weight:600;">Generating your workout...</div>
        </div>
    </div>
    <div class="container">
        <h1 class="mb-4 text-center" style="font-weight:800; color:#0077b6; letter-spacing:1px;">IntelliFit Workout Generator <i class="fa-solid fa-dumbbell"></i></h1>
        <div class="card p-4">
            <div class="form-title"><i class="fa-solid fa-person-running"></i> Create Your Personalized Workout</div>
            <form id="workoutForm">
                <div class="row g-3">
                    <div class="col-md-4">
                        <label for="skill_level" class="form-label">Skill Level</label>
                        <select class="form-select" id="skill_level" name="skill_level" required>
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label for="workout_goal" class="form-label">Workout Goal</label>
                        <select class="form-select" id="workout_goal" name="workout_goal" required>
                            <option value="weight loss">Weight Loss</option>
                            <option value="muscle building">Muscle Building</option>
                            <option value="maintenance">Maintenance</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label for="restrictions" class="form-label">Restrictions</label>
                        <input type="text" class="form-control" id="restrictions" name="restrictions" placeholder="e.g. no equipment, limited time">
                    </div>
                </div>
                <div class="mt-4 text-center">
                    <button type="submit" class="btn btn-primary btn-lg"><i class="fa-solid fa-bolt"></i> Generate Workout</button>
                </div>
            </form>
        </div>
        <div id="resultSection" style="display:none;">
            <div class="json-section" id="outputContent"></div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
    <script>
    document.getElementById('workoutForm').onsubmit = async function(e) {
        e.preventDefault();
        document.getElementById('resultSection').style.display = 'none';
        document.getElementById('loadingScreen').style.display = 'flex';
        const skill_level = document.getElementById('skill_level').value;
        const workout_goal = document.getElementById('workout_goal').value;
        const restrictions = document.getElementById('restrictions').value;
        const res = await fetch('/generate_workout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skill_level, workout_goal, restrictions })
        });
        const data = await res.json();
        let output = '';
        try {
            let result = data.result;
            // Remove markdown and parse JSON
            result = result.replace(/^```json|```$/g, '').trim();
            const workout = JSON.parse(result);
            output += `<h2 class='section-title'><i class='fa-solid fa-dumbbell icon'></i> ${workout.workout_name}</h2>`;
            output += `<div class='output-label'>Description:</div><div class='output-value mb-2'>${workout.description}</div>`;
            output += `<div class='row mb-2'><div class='col-md-4'><span class='output-label'><i class='fa-solid fa-clock icon'></i> Duration:</span> <span class='output-value'>${workout.total_duration_minutes} min</span></div>`;
            output += `<div class='col-md-4'><span class='output-label'><i class='fa-solid fa-signal icon'></i> Difficulty:</span> <span class='output-value'>${workout.difficulty_level}</span></div>`;
            output += `<div class='col-md-4'><span class='output-label'><i class='fa-solid fa-bullseye icon'></i> Goal:</span> <span class='output-value'>${workout.goal}</span></div></div>`;
            output += `<div class='output-label mt-3'><i class='fa-solid fa-ban icon'></i> Restrictions:</div> <div class='output-value'>${Array.isArray(workout.restrictions) ? workout.restrictions.join(', ') : workout.restrictions}</div>`;
            // Warm-up
            output += `<h4 class='section-title'><i class='fa-solid fa-fire icon'></i> Warm-Up (${workout.warm_up.duration_minutes} min)</h4><ul class='tips-list'>`;
            workout.warm_up.exercises.forEach(ex => {
                output += `<li><b>${ex.name}</b> (${ex.duration_seconds}s): ${ex.instructions}</li>`;
            });
            output += `</ul>`;
            // Main workout
            output += `<h4 class='section-title'><i class='fa-solid fa-dumbbell icon'></i> Main Workout</h4>`;
            output += `<div>Rounds: <b>${workout.main_workout.rounds}</b>, Rest Between Rounds: <b>${workout.main_workout.rest_between_rounds_seconds}s</b></div>`;
            output += `<ul class='tips-list'>`;
            workout.main_workout.exercises.forEach(ex => {
                output += `<li><b>${ex.name}</b> (${ex.reps_or_time}, Sets: ${ex.sets}, Rest: ${ex.rest_between_exercises_seconds}s)<br>Equipment: ${ex.equipment ? ex.equipment : 'None'}<br>${ex.instructions}`;
                if (ex.modifications) output += `<br><i>Modifications:</i> ${ex.modifications}`;
                output += `</li>`;
            });
            output += `</ul>`;
            // Finisher
            output += `<h4 class='section-title'><i class='fa-solid fa-flag-checkered icon'></i> Finisher (${workout.finisher.duration_minutes} min)</h4><ul class='tips-list'>`;
            workout.finisher.exercises.forEach(ex => {
                output += `<li><b>${ex.name}</b> (${ex.duration_seconds}s): ${ex.instructions}</li>`;
            });
            output += `</ul>`;
            // Equipment
            output += `<div class='output-label mt-3'><i class='fa-solid fa-toolbox icon'></i> Equipment Needed:</div><ul class='equipment-list'>`;
            workout.equipment_needed.forEach(eq => {
                output += `<li>${eq}</li>`;
            });
            output += `</ul>`;
            // Tips
            output += `<div class='output-label mt-3'><i class='fa-solid fa-lightbulb icon'></i> Tips:</div><ul class='tips-list'>`;
            workout.tips.forEach(tip => {
                output += `<li>${tip}</li>`;
            });
            output += `</ul>`;
            // Motivation
            output += `<div class='motivation'><i class='fa-solid fa-heart icon'></i> ${workout.motivation}</div>`;
        } catch (err) {
            output = `<div class='alert alert-danger'>Could not parse workout result. Raw output:</div><div class='json-raw'>${data.result}</div>`;
        }
        document.getElementById('outputContent').innerHTML = output;
        document.getElementById('resultSection').style.display = 'block';
        document.getElementById('loadingScreen').style.display = 'none';
    };
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.get_json()
    skill_level = data.get('skill_level', 'beginner')
    workout_goal = data.get('workout_goal', 'weight loss')
    restrictions = data.get('restrictions', 'no equipment')

    with open("/Users/pro/Desktop/GitHub Repos/IntelliFit/Planning/template.txt", "r") as f:
        template = f.read()

    template = re.sub(r"Skill level: \[beginner / intermediate / advanced\]", f"Skill level: {skill_level}", template)
    template = re.sub(r"Workout goal: \[weight loss / muscle building / maintenance\]", f"Workout goal: {workout_goal}", template)
    template = re.sub(r"Restrictions: \[e.g., no equipment / disabilities / limited time / etc.\]", f"Restrictions: {restrictions}", template)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=template
    )
    # Try to parse the output as JSON, else return as text
    try:
        output_json = response.text
        return jsonify({'result': output_json})
    except Exception as e:
        return jsonify({'error': str(e), 'raw_output': response.text}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)