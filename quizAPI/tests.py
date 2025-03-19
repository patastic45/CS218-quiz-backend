from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import QuizMulipleChoice, QuizTrueFalse, QuizCollection
# I used ChatGPT to give me sample test cases for the quiz API
class QuizAPITestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create test data
        self.multi_choice = QuizMulipleChoice.objects.create(
            owner=self.user, question="What is 2 + 2?", option1="3", option2="4", option3="5", option4="6", answer="2"
        )
        self.true_false = QuizTrueFalse.objects.create(
            owner=self.user, question="The earth is flat.", answer="0"
        )
        self.quiz_collection = QuizCollection.objects.create(
            title="Test Quiz Collection", owner=self.user
        )
        self.quiz_collection.multiQuestions.add(self.multi_choice)
        self.quiz_collection.trueFalseQuestions.add(self.true_false)

    ## ----------------------------- QUIZ MULTIPLE CHOICE ----------------------------- ##
    
    def test_create_quiz_multiple_choice(self):
        data = {
            "question": "What is the capital of France?",
            "option1": "Berlin",
            "option2": "Madrid",
            "option3": "Paris",
            "option4": "Rome",
            "answer": "2"
        }
        response = self.client.post("/multiple-choice-questions/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_quiz_multiple_choice(self):
        response = self.client.get(f"/multiple-choice-questions/{self.multi_choice.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question"], self.multi_choice.question)

    def test_update_quiz_multiple_choice(self):
        data = {"question": "Updated question?", "answer": "2"}
        response = self.client.patch(f"/multiple-choice-questions/{self.multi_choice.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.multi_choice.refresh_from_db()
        self.assertEqual(self.multi_choice.question, "Updated question?")

    def test_delete_quiz_multiple_choice(self):
        response = self.client.delete(f"/multiple-choice-questions/{self.multi_choice.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(QuizMulipleChoice.objects.filter(id=self.multi_choice.id).exists())

    ## ----------------------------- QUIZ TRUE/FALSE ----------------------------- ##

    def test_create_quiz_true_false(self):
        data = {"question": "The sky is blue.", "answer": "1"}
        response = self.client.post("/true-false-questions/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_quiz_true_false(self):
        response = self.client.get(f"/true-false-questions/{self.true_false.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question"], self.true_false.question)

    def test_update_quiz_true_false(self):
        data = {"question": "Updated True/False Question", "answer": "1"}
        response = self.client.patch(f"/true-false-questions/{self.true_false.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.true_false.refresh_from_db()
        self.assertEqual(self.true_false.question, "Updated True/False Question")

    def test_delete_quiz_true_false(self):
        response = self.client.delete(f"/true-false-questions/{self.true_false.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(QuizTrueFalse.objects.filter(id=self.true_false.id).exists())

    ## ----------------------------- QUIZ COLLECTION ----------------------------- ##
    
    def test_create_quiz_collection(self):
        data = {
            "title": "New Quiz Collection",
            "true_false_question_ids": [self.true_false.id],
            "multiple_choice_question_ids": [self.multi_choice.id]
        }
        response = self.client.post("/quiz-collections/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_quiz_collection(self):
        response = self.client.get(f"/quiz-collections/{self.quiz_collection.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.quiz_collection.title)

    def test_update_quiz_collection(self):
        data = {"title": "Updated Collection Title"}
        response = self.client.patch(f"/quiz-collections/{self.quiz_collection.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz_collection.refresh_from_db()
        self.assertEqual(self.quiz_collection.title, "Updated Collection Title")

    def test_delete_quiz_collection(self):
        response = self.client.delete(f"/quiz-collections/{self.quiz_collection.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(QuizCollection.objects.filter(id=self.quiz_collection.id).exists())

    ## ----------------------------- USER REGISTRATION ----------------------------- ##

    def test_user_registration(self):
        self.client.logout()
        data = {"username": "newuser", "password": "newpassword123"}
        response = self.client.post("/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())


class QuizAccessTests(APITestCase):
    
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        # Create multiple-choice and true/false questions owned by user1
        self.mc_question = QuizMulipleChoice.objects.create(
            owner=self.user1, question="What is 2+2?", option1="3", option2="4", option3="5", option4="6", answer=2
        )
        self.tf_question = QuizTrueFalse.objects.create(
            owner=self.user1, question="The sky is blue.", answer= "1"
        )

        # User 1's quiz collection containing the questions
        self.quiz_collection = QuizCollection.objects.create(title="User1's Quiz", owner=self.user1)
        self.quiz_collection.multiQuestions.add(self.mc_question)
        self.quiz_collection.trueFalseQuestions.add(self.tf_question)

        # Authenticate as user1
        self.client.login(username="user1", password="password123")

    def test_user2_cannot_access_user1_quiz(self):
        """Test that user2 cannot access user1's quiz collections"""
        self.client.logout()  # Log out user1
        self.client.login(username="user2", password="password123")  # Login as user2

        response = self.client.get(f"/quiz-collections/{self.quiz_collection.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # User2 should not see User1's quiz

    def test_user2_cannot_access_user1_multi_questions(self):
        """Test that user2 cannot access user1's quiz multiple-choice questions"""
        self.client.logout()  # Log out user1
        self.client.login(username="user2", password="password123")  # Login as user2

        response = self.client.get(f"/multiple-choice-questions/")

        self.assertEqual(response.data, [])  # User2 should not see User1's questions
    
    def test_user2_cannot_access_user1_truefalse_questions(self):
        """Test that user2 cannot access user1's quiz true/false questions"""
        self.client.logout()  # Log out user1
        self.client.login(username="user2", password="password123")  # Login as user2

        response = self.client.get(f"/true-false-questions/")

        self.assertEqual(response.data, [])  # User2 should not see User1's questions
    def test_user1_shares_quiz_with_user2(self):
        """Test that user1 can share a quiz collection with user2"""
        # Share the quiz collection with user2
        response = self.client.patch(
            f"/quiz-collections/{self.quiz_collection.id}/",
            {"shared_with": [self.user2.id]},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Logout user1 and login as user2
        self.client.logout()
        self.client.login(username="user2", password="password123")

        # User2 should now be able to access the shared quiz collection
        response = self.client.get(f"/quiz-collections/{self.quiz_collection.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.quiz_collection.id)  # Confirm it's the same quiz

    def test_user2_can_see_shared_questions(self):
        """Test that user2 can see User1’s multiple-choice and true/false questions when shared"""
        # Share quiz with user2
        self.client.patch(
            f"/quiz-collections/{self.quiz_collection.id}/",
            {"shared_with": [self.user2.id]},
            format="json"
        )

        # Logout user1 and login as user2
        self.client.logout()
        self.client.login(username="user2", password="password123")

        # User2 should be able to see the multiple-choice and true/false questions
        response = self.client.get(f"/quiz-collections/{self.quiz_collection.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if multiple-choice and true/false questions are present
        self.assertIn("multiple_choice_questions", response.data)
        self.assertIn("true_false_questions", response.data)

        self.assertEqual(len(response.data["multiple_choice_questions"]), 1)
        self.assertEqual(len(response.data["true_false_questions"]), 1)

        # Verify the actual content of the questions
        mc_question = response.data["multiple_choice_questions"][0]
        tf_question = response.data["true_false_questions"][0]

        self.assertEqual(mc_question["id"], self.mc_question.id)
        self.assertEqual(mc_question["question"], "What is 2+2?")
        self.assertEqual(mc_question["option 1"], "3")
        self.assertEqual(mc_question["option 2"], "4")

        self.assertEqual(tf_question["id"], self.tf_question.id)
        self.assertEqual(tf_question["question"], "The sky is blue.")


class QuizPermissionTests(APITestCase):
    
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        # Create multiple-choice and true/false questions owned by user1
        self.mc_question = QuizMulipleChoice.objects.create(
            owner=self.user1, question="What is 2+2?", option1="3", option2="4", option3="5", option4="6", answer=2
        )
        self.tf_question = QuizTrueFalse.objects.create(
            owner=self.user1, question="The sky is blue.", answer="1"
        )

        # User 1's quiz collection containing the questions
        self.quiz_collection = QuizCollection.objects.create(title="User1's Quiz", owner=self.user1)
        self.quiz_collection.multiQuestions.add(self.mc_question)
        self.quiz_collection.trueFalseQuestions.add(self.tf_question)

        # Authenticate as user1 and share the quiz with user2
        self.client.login(username="user1", password="password123")
        self.client.patch(
            f"/quiz-collections/{self.quiz_collection.id}/",
            {"shared_with": [self.user2.id]},
            format="json"
        )
        self.client.logout()

    def test_user2_cannot_update_user1_quiz(self):
        """Test that user2 cannot update User1's quiz collection"""
        self.client.login(username="user2", password="password123")

        response = self.client.patch(
            f"/quiz-collections/{self.quiz_collection.id}/",
            {"title": "Hacked Quiz"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Should not be allowed
        self.quiz_collection.refresh_from_db()
        self.assertNotEqual(self.quiz_collection.title, "Hacked Quiz")  # Ensure title did not change

    def test_user2_cannot_delete_user1_quiz(self):
        """Test that user2 cannot delete User1's quiz collection"""
        self.client.login(username="user2", password="password123")

        response = self.client.delete(f"/quiz-collections/{self.quiz_collection.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Should not be allowed
        self.assertTrue(QuizCollection.objects.filter(id=self.quiz_collection.id).exists())  # Quiz should still exist

    def test_user2_cannot_add_questions_to_user1_quiz(self):
        """Test that user2 cannot add questions to User1's quiz collection"""
        self.client.login(username="user2", password="password123")

        new_mc_question = QuizMulipleChoice.objects.create(
            owner=self.user2, question="What is 3+3?", option1="5", option2="6", option3="7", option4="8", answer=2
        )

        response = self.client.patch(
            f"/quiz-collections/{self.quiz_collection.id}/",
            {"multiple_choice_question_ids": [new_mc_question.id]},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Should not be allowed
        self.assertNotIn(new_mc_question, self.quiz_collection.multiQuestions.all())  # Ensure question wasn't added

