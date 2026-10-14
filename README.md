# Poll System - Poll Service

A FastAPI microservice responsible for managing poll questions, customer answers, and analytics reporting.

## Architecture
- **Framework**: FastAPI (Python 3.12)
- **Database**: MySQL 8.0 (using SQLAlchemy ORM)
- **Pattern**: MVC / Layered Architecture (`Controller` -> `Service` -> `Repository` -> `Model`)
- **Validation**: Pydantic v2 Request/Response models

## Features & Business Rules
1. **Questions CRUD**:
   - Create, Read, Update, Delete questions.
   - **Update Restriction**: A question *cannot* be updated if users have already answered it (returns `400 Bad Request`), unless all user answers are deleted first.
   - **Cascade Deletion**: Deleting a question automatically cascades and deletes all submitted answers.
2. **Answers Management**:
   - **Registration Enforcement**: Poll Service verifies with User Service that the user exists and `is_registered == True`. If unregistered, answering is rejected (`403 Forbidden`).
   - **One Answer per Question**: Users can only submit one answer per question (`409 Conflict` on duplicate submission).
   - **Update Answer**: Dedicated `PUT /answers/{answer_id}` endpoint to update the selected option.
   - **Delete Answer**: `DELETE /answers/{answer_id}` endpoint.
   - **Inter-service Cascade**: `DELETE /answers/user/{user_id}` removes all answers submitted by a deleted user.
3. **Analytics & Reporting (5 Endpoints)**:
   - `GET /analytics/questions/{question_id}/options-count`: Users count per option.
   - `GET /analytics/questions/{question_id}/total-answers`: Total answers count for a question.
   - `GET /analytics/users/{user_id}/answers`: List of questions and chosen answers for a user.
   - `GET /analytics/users/{user_id}/total-answers`: Total questions answered by a user.
   - `GET /analytics/global-summary`: All questions, all options, and answer distribution.

## API Endpoints (Base URL: `/api/v1`)
| Group | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Questions** | `POST` | `/questions` | Create question (with 4 options) |
| | `GET` | `/questions` | List questions (supports `skip`, `limit`) |
| | `GET` | `/questions/{id}` | Get question by ID |
| | `PUT` | `/questions/{id}` | Update question (blocked if answered) |
| | `DELETE`| `/questions/{id}` | Delete question (cascades answers) |
| **Answers** | `POST` | `/answers` | Submit answer (requires registered user) |
| | `PUT` | `/answers/{id}` | Update answer choice |
| | `DELETE`| `/answers/{id}` | Delete answer by ID |
| | `DELETE`| `/answers/user/{user_id}` | Internal hook to delete all answers by user |
| **Analytics** | `GET` | `/analytics/questions/{id}/options-count` | Count per option for question |
| | `GET` | `/analytics/questions/{id}/total-answers` | Total answers for question |
| | `GET` | `/analytics/users/{user_id}/answers` | All answers by user |
| | `GET` | `/analytics/users/{user_id}/total-answers` | Count of questions answered by user |
| | `GET` | `/analytics/global-summary` | Complete summary across all polls |

## Running Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

## Running with Docker
```bash
docker build -t poll-poll-service .
docker run -p 8002:8002 poll-poll-service
```
Interactive API documentation is accessible at `http://localhost:8002/docs`.
