# Article Recommendation & Analytics Engine

A Python Flask web application that logs user interaction events (views, likes, time spent) and uses them to generate article recommendations and analytics dashboards.  
The system also includes an A/B Testing Dashboard to compare Popularity-based and Content-based recommendation strategies.

## Team
Meriton Gashi  
Albion Sutaj  
Adonis Hajdaraj  

## Features
- Interaction event logging: views, likes, time spent  
- Recommendation strategies:
  - Popularity-based recommendation  
  - Content-based recommendation  
- Analytics dashboard with engagement metrics  
- A/B Testing Dashboard with CTR-based comparison  
- Layered architecture with Service and Repository patterns  
- Strategy and Factory design patterns  
- TF-IDF keyword extraction for content analysis  
- Unit tests for recommendation strategies  

## Tech Stack
- Python 3  
- Flask  
- SQLite  
- Jinja2  
- Scikit-learn (TF-IDF)  
- HTML & CSS  
- Pytest / unittest  

## Project Structure
app/
main.py # Flask app, routes, A/B logic
services/ # Business logic
article_service.py
interaction_event_service.py
recommendation_factory.py
recommendation_strategies.py
repositories/ # Data access layer
static/css/style.css
templates/
base.html
home.html
article_detail.html
recommendations.html
analytics.html
ab_dashboard.html
tests/
test_recommendation_strategies.py
run.py
app.db
requirements.txt
README.md

markdown
Copy code

## Architecture Overview

The system follows a layered architecture:

### 1. Presentation Layer
Flask web pages rendered with Jinja2:
- Home page  
- Article detail page  
- Recommendations page  
- Analytics dashboard  
- A/B Testing dashboard  

### 2. API Layer
Flask routes provide REST-like endpoints:
- `/api/events` for logging interaction events  
- `/api/recommendations/<id>` for recommendation results  
- `/api/analytics/<id>` for analytics data  
- `/api/ab-summary` for A/B statistics  

### 3. Application / Domain Layer
Service classes implement core logic:
- ArticleService  
- InteractionEventService  
- Recommendation strategies  
- Analytics calculations  

### 4. Data Access Layer
Repositories and SQLite handle:
- Articles  
- Categories  
- Interaction events  

This separation improves maintainability, scalability, and testability.

## Design Patterns Used

### Strategy Pattern
Two recommendation strategies:
- Popularity-based  
- Content-based  

They can be switched without changing the main system logic.

### Factory Pattern
`RecommendationFactory` dynamically creates the selected recommendation strategy.

### Repository Pattern
All database logic is isolated from business logic.

## Recommendation Algorithms

### Popularity-Based
Uses engagement signals:
- Views  
- Likes  
- Time spent  

Best for trending content and cold-start users.

### Content-Based
Uses TF-IDF to analyze:
- Article titles  
- Content  
- Categories  

Recommends similar articles based on keyword similarity.

## A/B Testing Dashboard

Each browser session is randomly assigned to:

- Group A → Popularity-based strategy  
- Group B → Content-based strategy  

### Winner Selection Rules
1. Compare CTR = Likes ÷ Views  
2. If CTR is equal, compare Time Spent  
3. If still equal, Group A wins by default  

### Purpose
This allows objective comparison of algorithm performance using real interaction data.

## Main Routes

| Route | Description |
|------|------------|
| / | Home page |
| /articles/<id> | Article details + auto view logging |
| /recommendations | Recommendation UI |
| /analytics | Analytics dashboard |
| /ab-dashboard | A/B Testing dashboard |
| /api/events | Log view, like, time spent |
| /api/recommendations/<id> | API recommendations |
| /api/analytics/<id> | API analytics |
| /api/ab-summary | A/B summary API |

## How to Run

Install dependencies (without []) 
[```bash
pip install -r requirements.txt]

Run the app python: 
run.py.

Open in browser: 
http://127.0.0.1:5050/. 

For testing, run: 
pytest
