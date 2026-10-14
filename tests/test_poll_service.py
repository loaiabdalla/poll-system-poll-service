"""Comprehensive integration and logic tests for Poll Service."""
from unittest.mock import AsyncMock, patch
from fastapi import status


def test_question_crud_and_update_restriction(client):
    # 1. Create a question
    q_payload = {
        "title": "Between the following, what do you most love to do?",
        "option_1": "Watch TV",
        "option_2": "Play the computer",
        "option_3": "Hanging out with friends",
        "option_4": "Travel the world",
    }
    create_res = client.post("/api/v1/questions", json=q_payload)
    assert create_res.status_code == status.HTTP_201_CREATED
    q_data = create_res.json()
    q_id = q_data["id"]
    assert q_data["title"] == q_payload["title"]

    # 2. Update question before any answer -> Should succeed
    update_res = client.put(f"/api/v1/questions/{q_id}", json={"title": "Updated question title?"})
    assert update_res.status_code == status.HTTP_200_OK
    assert update_res.json()["title"] == "Updated question title?"

    # 3. Submit an answer (mocking UserClient returning registered user)
    with patch("app.services.user_client.UserClient.get_user", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = {"id": 1, "is_registered": True}
        ans_res = client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 1, "selected_option": 2})
        assert ans_res.status_code == status.HTTP_201_CREATED
        ans_id = ans_res.json()["id"]

    # 4. Attempt to update question after being answered -> MUST FAIL WITH 400
    blocked_update = client.put(f"/api/v1/questions/{q_id}", json={"title": "Should be blocked"})
    assert blocked_update.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot be updated because users have already submitted answers" in blocked_update.json()["detail"]

    # 5. Delete the user answer
    del_ans_res = client.delete(f"/api/v1/answers/{ans_id}")
    assert del_ans_res.status_code == status.HTTP_204_NO_CONTENT

    # 6. Now update should be permitted again
    unblocked_update = client.put(f"/api/v1/questions/{q_id}", json={"title": "Unblocked update title"})
    assert unblocked_update.status_code == status.HTTP_200_OK
    assert unblocked_update.json()["title"] == "Unblocked update title"


def test_answer_registration_enforcement_and_uniqueness(client):
    # Create question
    q_res = client.post("/api/v1/questions", json={
        "title": "Where is your preferred place to travel?",
        "option_1": "USA",
        "option_2": "France",
        "option_3": "South America",
        "option_4": "Thailand",
    })
    q_id = q_res.json()["id"]

    # Case A: User does not exist in User Service -> 404
    with patch("app.services.user_client.UserClient.get_user", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = None
        res_404 = client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 999, "selected_option": 1})
        assert res_404.status_code == status.HTTP_404_NOT_FOUND

    # Case B: User exists but is NOT registered -> 403 Forbidden
    with patch("app.services.user_client.UserClient.get_user", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = {"id": 2, "is_registered": False}
        res_403 = client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 2, "selected_option": 1})
        assert res_403.status_code == status.HTTP_403_FORBIDDEN
        assert "not registered" in res_403.json()["detail"]

    # Case C: User is registered -> 201 Created
    with patch("app.services.user_client.UserClient.get_user", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = {"id": 3, "is_registered": True}
        res_201 = client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 3, "selected_option": 2})
        assert res_201.status_code == status.HTTP_201_CREATED
        ans_id = res_201.json()["id"]

        # Case D: Same user attempts to answer again -> 409 Conflict
        res_409 = client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 3, "selected_option": 3})
        assert res_409.status_code == status.HTTP_409_CONFLICT

    # Case E: Update answer by answer ID -> 200 OK
    update_ans_res = client.put(f"/api/v1/answers/{ans_id}", json={"selected_option": 4})
    assert update_ans_res.status_code == status.HTTP_200_OK
    assert update_ans_res.json()["selected_option"] == 4


def test_question_deletion_cascades_answers(client):
    # Create question
    q_res = client.post("/api/v1/questions", json={
        "title": "Favorite season?",
        "option_1": "Spring",
        "option_2": "Summer",
        "option_3": "Autumn",
        "option_4": "Winter",
    })
    q_id = q_res.json()["id"]

    # Submit answer
    with patch("app.services.user_client.UserClient.get_user", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = {"id": 5, "is_registered": True}
        ans_res = client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 5, "selected_option": 1})
        ans_id = ans_res.json()["id"]

    # Delete question
    del_q_res = client.delete(f"/api/v1/questions/{q_id}")
    assert del_q_res.status_code == status.HTTP_204_NO_CONTENT

    # Answer should be deleted via cascade
    del_ans_res = client.delete(f"/api/v1/answers/{ans_id}")
    assert del_ans_res.status_code == status.HTTP_404_NOT_FOUND


def test_analytics_and_statistics_endpoints(client):
    # Setup question
    q_res = client.post("/api/v1/questions", json={
        "title": "Which coffee roast do you prefer?",
        "option_1": "Light Roast",
        "option_2": "Medium Roast",
        "option_3": "Dark Roast",
        "option_4": "Decaf",
    })
    q_id = q_res.json()["id"]

    # Simulate 3 users answering
    with patch("app.services.user_client.UserClient.get_user", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = {"is_registered": True}
        # User 10 chooses Option 1
        client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 10, "selected_option": 1})
        # User 20 chooses Option 1
        client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 20, "selected_option": 1})
        # User 30 chooses Option 3
        client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 30, "selected_option": 3})

    # Requirement 1: Options distribution for question
    dist_res = client.get(f"/api/v1/analytics/questions/{q_id}/options-count")
    assert dist_res.status_code == status.HTTP_200_OK
    dist_data = dist_res.json()
    assert dist_data["question_id"] == q_id
    options_map = {opt["option_number"]: opt["count"] for opt in dist_data["options"]}
    assert options_map[1] == 2
    assert options_map[2] == 0
    assert options_map[3] == 1
    assert options_map[4] == 0

    # Requirement 2: Total answers for question
    total_q_res = client.get(f"/api/v1/analytics/questions/{q_id}/total-answers")
    assert total_q_res.status_code == status.HTTP_200_OK
    assert total_q_res.json()["total_answers"] == 3

    # Requirement 3: User's answers
    user_answers_res = client.get("/api/v1/analytics/users/10/answers")
    assert user_answers_res.status_code == status.HTTP_200_OK
    user_answers = user_answers_res.json()
    assert user_answers["user_id"] == 10
    assert len(user_answers["answers"]) == 1
    assert user_answers["answers"][0]["selected_option"] == 1
    assert user_answers["answers"][0]["selected_option_text"] == "Light Roast"

    # Requirement 4: Total questions answered by user
    user_total_res = client.get("/api/v1/analytics/users/10/total-answers")
    assert user_total_res.status_code == status.HTTP_200_OK
    assert user_total_res.json()["total_questions_answered"] == 1

    # Requirement 5: Global statistics
    global_res = client.get("/api/v1/analytics/global-summary")
    assert global_res.status_code == status.HTTP_200_OK
    global_data = global_res.json()
    assert global_data["total_questions"] >= 1


def test_internal_delete_all_answers_by_user(client):
    # Setup question
    q_res = client.post("/api/v1/questions", json={
        "title": "Favorite cloud provider?",
        "option_1": "GCP",
        "option_2": "AWS",
        "option_3": "Azure",
        "option_4": "On-prem",
    })
    q_id = q_res.json()["id"]

    # Submit answer for user 55
    with patch("app.services.user_client.UserClient.get_user", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = {"id": 55, "is_registered": True}
        client.post("/api/v1/answers", json={"question_id": q_id, "user_id": 55, "selected_option": 1})

    # Call internal cascade endpoint
    cascade_res = client.delete("/api/v1/answers/user/55")
    assert cascade_res.status_code == status.HTTP_200_OK
    assert cascade_res.json()["deleted_count"] == 1

    # Check that user 55 has 0 answers now
    user_total = client.get("/api/v1/analytics/users/55/total-answers")
    assert user_total.json()["total_questions_answered"] == 0
