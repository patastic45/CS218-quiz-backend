from rest_framework import serializers
from quizAPI.models import QuizCollection, QuizMulipleChoice, QuizTrueFalse, QuizCollectionAnswer
from django.contrib.auth.models import User

# serializer for multiple choice questions
# allows user to create and view multiple choice questions
# also allows user to add a question to a collection

class QuizMultipleChoiceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    answer = serializers.ChoiceField(choices=[1, 2, 3, 4])
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=QuizCollection.objects.all(), required=False, write_only=True, allow_null=True, allow_empty=True
    )
    class Meta:
        model = QuizMulipleChoice
        # fields = ['id', 'question', 'option1', 'option2', 'option3', 'option4', 'answer']
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['collection_id'].queryset = QuizCollection.objects.filter(owner=request.user)


    def create(self, validated_data):
        collection = validated_data.pop('collection_id', None)
        question = QuizMulipleChoice.objects.create(**validated_data)

        if collection:
            collection.multiQuestions.add(question)

        return question

# serializer for true false questions
# allows user to create and view true false questions
# also allows user to add a question to a collection
class QuizTrueFalseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    answer = serializers.ChoiceField(choices=[True, False])
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=QuizCollection.objects.all(), required=False, write_only=True, allow_null=True, allow_empty=True
    )
    class Meta:
        model = QuizTrueFalse
        # fields = ['id', 'question', 'answer']
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['collection_id'].queryset = QuizCollection.objects.filter(owner=request.user)

        
    def create(self, validated_data):
        collection = validated_data.pop('collection_id', None)
        question = QuizTrueFalse.objects.create(**validated_data)

        if collection:
            collection.trueFalseQuestions.add(question)

        return question



# serializer for user
# allows user to create an account to use other endpoints
# This currently uses Django's built-in User model
# in future, I would want to use something like 0Auth2 to allow users to log in with their Google
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    multi = serializers.PrimaryKeyRelatedField(many=True, queryset=QuizMulipleChoice.objects.all(), required=False)
    truefalse = serializers.PrimaryKeyRelatedField(many=True, queryset=QuizTrueFalse.objects.all(), required=False)
    collection = serializers.PrimaryKeyRelatedField(many=True, queryset=QuizCollection.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'multi', 'truefalse', 'collection', 'password']

    def create(self, validated_data):
        multi_data = validated_data.pop('multi', [])  # Extract multi-question IDs
        truefalse_data = validated_data.pop('truefalse', [])  # Extract true-false question IDs
        collection = validated_data.pop('collection', [])  # Extract collection IDs

        user = User.objects.create_user(**validated_data)  # Create user first

        if isinstance(multi_data, list):
            user.multi.set([])  # Set the multiple choice questions

        if isinstance(truefalse_data, list):
            user.truefalse.set([])  # Set the true-false questions

        if isinstance(collection, list):
            user.collection.set([]) # Set the collection
        return user
    

    def get_multi(self, obj):
        request = self.context.get("request")
        if request and request.user.is_staff:
            return [quiz.id for quiz in obj.quizmuliplechoice_set.all()]
        return []  # Hide for non-admins

    def get_truefalse(self, obj):
        request = self.context.get("request")
        if request and request.user.is_staff:
            return [quiz.id for quiz in obj.quiztruefalse_set.all()]
        return []

# serializer for quiz collection
# allows user to create a collection of questions
# also allows user to add questions to a collection
# also allows user to share a collection with other users
class QuizCollectionSerializer(serializers.ModelSerializer):
    true_false_questions = serializers.SerializerMethodField()
    multiple_choice_questions = serializers.SerializerMethodField()

    # Allow adding questions by ID when updating or creating
    true_false_question_ids = serializers.PrimaryKeyRelatedField(
        queryset=QuizTrueFalse.objects.all(), many=True, write_only=True, required=False
    )
    multiple_choice_question_ids = serializers.PrimaryKeyRelatedField(
        queryset=QuizMulipleChoice.objects.all(), many=True, write_only=True, required=False
    )

    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = QuizCollection
        fields = [
            'id', 'title', 'owner', 
            'true_false_questions', 'multiple_choice_questions', 
            'true_false_question_ids', 'multiple_choice_question_ids',
            'shared_with'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['true_false_question_ids'].queryset = QuizTrueFalse.objects.filter(owner=request.user)
            self.fields['multiple_choice_question_ids'].queryset = QuizMulipleChoice.objects.filter(owner=request.user)
            self.fields['true_false_questions'].queryset = QuizTrueFalse.objects.filter(owner=request.user)
            self.fields['multiple_choice_questions'].queryset = QuizMulipleChoice.objects.filter(owner=request.user)

    # hide answers from shared users
    def get_true_false_questions(self, obj):
            request = self.context.get("request")
            if request and obj.owner == request.user:
                return QuizTrueFalseSerializer(obj.trueFalseQuestions.all(), many=True).data
            else:
                return [{"id": q.id, "question": q.question} for q in obj.trueFalseQuestions.all()]
            
    # hide answers from shared users
    def get_multiple_choice_questions(self, obj):
        request = self.context.get("request")
        if request and obj.owner == request.user:
            return QuizMultipleChoiceSerializer(obj.multiQuestions.all(), many=True).data
        else:
            return [
                {
                    "id": q.id,
                    "question": q.question,
                    "option 1": q.option1,
                    "option 2": q.option2,
                    "option 3": q.option3,
                    "option 4": q.option4,
                }
                for q in obj.multiQuestions.all()
            ]
    
    # I asked chatGPT on how to validate as I was having issues with the list of ids
    def validate_multiple_choice_question_ids(self, value):
        if not isinstance(value, list):  # Ensure it's a list
            raise serializers.ValidationError("Expected a list of multiple-choice question IDs.")
        
        # Ensure all elements in the list are either integers or queryset objects
        if not all(isinstance(item, (int, QuizMulipleChoice)) for item in value):
            raise serializers.ValidationError("All multiple-choice question IDs must be integers or valid question instances.")
        
        # Convert queryset objects to IDs (if they exist)
        return [item.id if isinstance(item, QuizMulipleChoice) else item for item in value]

    # I asked chatGPT on how to validate as I was having issues with the list of ids
    def validate_true_false_question_ids(self, value):
        if not isinstance(value, list):  # Ensure it's a list
            raise serializers.ValidationError("Expected a list of true/false question IDs.")
        
        if not all(isinstance(item, (int, QuizTrueFalse)) for item in value):
            raise serializers.ValidationError("All question IDs must be integers or valid question instances.")
        
        return [item.id if isinstance(item, QuizTrueFalse) else item for item in value]
    
    def validate_shared_with(self, value):
        """Ensure users are not adding themselves or the owner again."""
        owner = self.context['request'].user
        if owner in value:
            raise serializers.ValidationError("You cannot add yourself to shared users.")
        return value

    def create(self, validated_data):
        request_user = self.context['request'].user  # Get the current logged-in user
        if not request_user or not request_user.is_authenticated:
            raise serializers.ValidationError("You must be logged in to create a quiz collection.")

        true_false_ids = validated_data.pop('true_false_question_ids', [])
        multiple_choice_ids = validated_data.pop('multiple_choice_question_ids', [])
        shared_user_ids = validated_data.pop('shared_with', [])  
        print(multiple_choice_ids)
        quiz_collection = QuizCollection.objects.create(**validated_data)

        # Ensure questions belong to the current user before adding them
        true_false_questions = QuizTrueFalse.objects.filter(id__in=true_false_ids, owner=request_user)
        multiple_choice_questions = QuizMulipleChoice.objects.filter(id__in=multiple_choice_ids, owner=request_user)
        #shared_users = User.objects.filter(id__in=shared_user_ids) 
        print(true_false_questions)

        quiz_collection.trueFalseQuestions.set(true_false_questions)
        quiz_collection.multiQuestions.set(multiple_choice_questions)
        quiz_collection.shared_with.set(shared_user_ids)
        return quiz_collection

    def update(self, instance, validated_data):
        request_user = self.context['request'].user  # Get the current logged-in user
        if not request_user or not request_user.is_authenticated:
            raise serializers.ValidationError("You must be logged in to create a quiz collection.")

        true_false_ids = validated_data.pop('true_false_question_ids', [])
        multiple_choice_ids = validated_data.pop('multiple_choice_question_ids', [])


        instance.title = validated_data.get('title', instance.title)

        # Filter only questions owned by the current user
        if true_false_ids:
            true_false_questions = QuizTrueFalse.objects.filter(id__in=true_false_ids, owner=request_user)
            instance.trueFalseQuestions.add(*true_false_questions)

        if multiple_choice_ids:
            multiple_choice_questions = QuizMulipleChoice.objects.filter(id__in=multiple_choice_ids, owner=request_user)
            instance.multiQuestions.add(*multiple_choice_questions)


        shared_user_ids = validated_data.pop('shared_with', [])  # Extract list of user IDs, not objects  
        if isinstance(shared_user_ids, list) and all(isinstance(id, int) for id in shared_user_ids):  
            shared_users = User.objects.filter(id__in=shared_user_ids) 
        instance.shared_with.set(shared_user_ids) 



        #instance.shared_with.add(*shared_user_ids)  # Assign using IDs
        instance.save()
        return instance
    
class QuizCollectionAnswerSerializer(serializers.ModelSerializer):
    multiQuizID = serializers.PrimaryKeyRelatedField(
        queryset=QuizMulipleChoice.objects.all(), many=True
    )
    trueFalseQuizID = serializers.PrimaryKeyRelatedField(
        queryset=QuizTrueFalse.objects.all(), many=True
    )

    class Meta:
        model = QuizCollectionAnswer
        fields = ['collectionID', 'multiQuizID', 'trueFalseQuizID', 'answers', 'score']

class QuizCollectionAnswerSerializer(serializers.ModelSerializer):
    multiQuizID = serializers.PrimaryKeyRelatedField(
        queryset=QuizMulipleChoice.objects.all(), many=True
    )
    trueFalseQuizID = serializers.PrimaryKeyRelatedField(
        queryset=QuizTrueFalse.objects.all(), many=True
    )
    answers = serializers.JSONField()  # Store answers in JSON format

    class Meta:
        model = QuizCollectionAnswer
        fields = ['collectionID', 'multiQuizID', 'trueFalseQuizID', 'answers', 'score']

    def create(self, validated_data):
        request = self.context['request']
        collection = validated_data['collectionID']

        # Assign the owner automatically based on the quiz collection
        validated_data['owner'] = collection.owner

        # Extract quiz IDs before saving
        multi_quizzes = validated_data.pop('multiQuizID', [])
        tf_quizzes = validated_data.pop('trueFalseQuizID', [])
        answers = validated_data.pop('answers', {})

        # Validate answers based on quiz IDs
        score = 0  # Start with 0 score
        correct_answers = {}
        total_questions = len(multi_quizzes) + len(tf_quizzes)

        # Validate Multiple Choice Answers
        for quiz in multi_quizzes:
            answer_key = f"MC_{quiz.id}"
            if answer_key in answers and int(answers[answer_key]) == quiz.answer:
                score += 1
                correct_answers[answer_key] = quiz.answer

        # Validate True/False Answers
        for quiz in tf_quizzes:
            answer_key = f"TF_{quiz.id}"
            if answer_key in answers and int(answers[answer_key]) == quiz.answer:
                score += 1
                correct_answers[answer_key] = quiz.answer

 
        collectionUpdate=QuizCollection.objects.filter(id=collection.id)
        collectionUpdate.first().answered.add(request.user)

        # Store calculated score
        print(score)
        validated_data['score'] = score/total_questions * 100 if total_questions > 0 else 0
        validated_data['answers'] = answers  # Store original answers

        # Create the answer instance
        answer_instance = super().create(validated_data)

        # Assign multiple-choice and true/false quizzes
        answer_instance.multiQuizID.set(multi_quizzes)
        answer_instance.trueFalseQuizID.set(tf_quizzes)

        return answer_instance