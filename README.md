# CS218-QuizAPI

 disclaimer- please ignore the ReactFrontEnd I got ahead of myself

 This API contains 4 major models

 QuizMultipleChoice, QuizTrueFalse, QuizCollection, and Django's User.

 QuizMultiple Choice has a structure of: <br />

 {
    "answer": null,         This is the answer 1-4 <br />
    "collection_id": null,  Allows you to assign to a quiz collection if you have one <br />
    "question": "",         The question   <br />
    "option1": "",          quiz answer options <br />
    "option2": "",          <br />
    "option3": "",          <br />
    "option4": ""           <br />
}

This can be accessed from the endpoint: /multiple-choice-questions:<br />
this end point allows you to see all QuizMultiple associated with the current logged in user
and post new entries

multiple-choice-questions/[id]:<br />
this end point lets you perform CRUD operations on the current entry

QuizTrueFalse has a structure of: <br />
{
    "answer": null,         This is 0 or 1 for false/true <br />
    "collection_id": null,  Allows you to assign this quiz collection if you have one <br />
    "question": ""          True false question <br />
}

This can be accessed from the endpoint: /true-false-questions: <br />
this end point allows you to see all QuizTrueFalse associated with the current logged in user
and post new entries

and true-false-questions/[id]: <br />
this end point lets you perform CRUD operations on the current entry

QuizCollection has a structure of: <br />
{
    "title": "",                        Title of quiz <br />
    "true_false_question_ids": [],      Add Ids of true false questions that belong to current user <br />
    "multiple_choice_question_ids": [], Add Ids of multi choice questions that belong to current user <br />
    "shared_with": []                   Add Ids of other users to share this quiz collection with them <br />
}

This can be accessed from the endpoint: /quiz-collection:<br />
this end point allows you to see all QuizCollection associated with the current logged in user
and post new entries

and true-false-questions/[id]:<br />
this end point lets you perform CRUD operations on the current entry if you own the ID

and true-false-questions/[id]:<br />
where id is an id of a collection shared to you, you will only be able to view it.

Django's User is a model that comes with Django, it provides a very simple auth by loging in at this endpoint <br />
/api-auth/login/

Before that you must create a user at this end point<br />
/register/
which takes:<br />
{
    "username": "",     username<br />
    "multi": [],        multi ids asscoiated with this user<br />
    "truefalse": [],    true false ids associate with this user<br />
    "password": ""      userpassword<br />
}

you should just post <br />
{
    "username": "your_username"<br />
    "password": "your_password"<br />
}

you can fill in multi and truefalse, but they should be discarded by the API

the endpoint /users/ and /users/<int:pk>/<br />
just shows the user currently logged in and all the enrty ids associated with them


# My Design Thoughts

I thought that the user should be able to create questions like the multiple choice and
true false questions as quizzes. So, I started with creating the two models.

Then I thought about how only 1 question doesn't make a great quiz, so I came up with the quiz collection
model.

Then came the thought of Auth and making sure users can change other users quizzes and collections.

Lastly, I thought about how users will be able to access other users collections, which lead me to make
the share with field.

# General work flow

I would expect the user to go to /register/ to create their account and login<br />
Then they can create questions and collections at the predefined endpoints.<br />
They can then share their collection with other users to take the quiz, which<br />
would be done in a Frontend. I would ideally have a different table that tracks<br />
the user's score or answers for the questions as well.<br />

