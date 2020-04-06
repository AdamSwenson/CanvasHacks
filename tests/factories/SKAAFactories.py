"""
These actually populate assignments in the
canvas sandbox with test data

Created by adam on 1/22/20
"""
import canvasapi

__author__ = 'adam'

if __name__ == '__main__':
    pass

from CanvasHacks.Models.users import StudentUser
from faker import Faker

fake = Faker()

# ------------------------------ Survey answer tools
import random

def answer_essay_survey_questions( questions):
    # make answers
    answers = []
    for q in questions:
        answers.append({
            'id' : q.id,
            'answer': "\n".join([fake.paragraph() for _ in range(0,5)])
        })
    return answers

def answer_multiple_choice_survey_questions(questions):
    answers = []
    for q in questions:
        choices = q.answers
        random.shuffle(choices)
        answers.append({
            'id': q.id,
            'answer': choices[0]['id']
        })
    return answers


def answer_survey(student_token, course_id, quiz_id, essay_questions, multiple_choice):
    student = StudentUser(student_token, course_id, quiz_id=quiz_id)
    quiz = student.course.get_quiz(quiz_id)

    # Create a submission object
    try:
        submission = quiz.create_submission()
    except canvasapi.exceptions.Conflict:
        # a submission was already created
        # so get that one
        submission = [s for s in quiz.get_submissions()][0]

    # make answers
    answers = []
    answers += answer_essay_survey_questions(essay_questions)
    answers += answer_multiple_choice_survey_questions(multiple_choice)

    # submit answers
    question_subs = submission.answer_submission_questions(quiz_questions=answers)

    # Complete the quiz
    submission.complete()
    print("Answers created for user {}".format(submission.user_id))

    # return for use in testing
    return answers



# ------------------------------- Discussion answer tools

def populate_discussion( tokens: list, topic_id: int, deep: int, course_id: int ):
    """Uploads test data to a discussion forum
    :param topic_id: The identifier of the canvas discussion to populate
    :param deep: The number of mutual replies to each post
    :param course_id: The canvas id of the course
    :param tokens: List of student access token strings
    """
    posts = [ ]
    student_users = [ ]
    for t in tokens:
        student_users.append( StudentUser( t, course_id, topic_id=topic_id ) )

    for su in student_users:
        msg = fake.paragraph()
        e = su.post_entry( msg )
        posts.append( e )
    for i in range( 0, deep ):
        for s1 in student_users:
            for entry in s1.discussion_entries:
                # every other student comments on each entry
                for s2 in student_users:
                    msg = fake.paragraph()
                    e = s2.discussion.get_entries( [ entry.id ] )
                    r = e[ 0 ].post_reply( message=msg )
                    posts.append( r )


# ---------------------- Assignment answer tools

def populate_assignment( tokens: list, assignment_id: int, course_id: int, num_paragraphs=1 ):
    """Uploads a paragraph of response text for each token provided
    in tokens.
    :param assignment_id: The identifier of the canvas unit to populate
    :param course_id: The canvas id of the course
    :param tokens: List of student access token strings
    :returns List of Submission objects returned from server
    """
    submissions = [ ]

    for t in tokens:
        msg = '\n '.join([fake.paragraph() for _ in range(0,num_paragraphs)])
        sub = {
            'submission_type': 'online_text_entry',
            'body': msg,
        }
        s1 = StudentUser( t, course_id, assignment_id=assignment_id )
        result = s1.assignment.submit( sub )
        submissions.append( result )
    return submissions


# -------------------- Quiz answer tools
def get_question_ids( course, quiz_id ):
    """Returns list of ids for questions comprising quiz"""
    qids = [ q.id for q in course.get_quiz( quiz_id ).get_questions() ]
    print( "{} question ids retrieved for quiz {}".format( len( qids ), quiz_id ) )
    return qids


def answer_quiz_for_student( student_token, course_id, quiz_id, question_ids ):
    """Answers all quiz questions for one student"""
    student = StudentUser( student_token, course_id, quiz_id=quiz_id )
    quiz = student.course.get_quiz( quiz_id )

    # Create a submission object
    try:
        submission = quiz.create_submission()
    except canvasapi.exceptions.Conflict:
        # a submission was already created
        # so get that one
        submission = [ s for s in quiz.get_submissions() ][ 0 ]

    # make answers
    answers = [ ]
    for qid in question_ids:
        answers.append( {
            'id': qid,
            'answer': fake.paragraph()
        } )

    # submit answers
    question_subs = submission.answer_submission_questions( quiz_questions=answers )

    # Complete the quiz
    submission.complete()
    print( "Answers created for user {}".format( submission.user_id ) )

    # return quizSubmissionQuestions for use in testing
    # answer text will be stored on answer attribute
    return question_subs


def populate_quiz_w_text_answers( course, quiz_id, student_tokens ):
    """
    Answers all text entry questions for a quiz for all students

    Returns a list of QuizSubmissionQuestions which contains the answer text
    in answer attribute"""
    answers = [ ]
    question_ids = get_question_ids( course, quiz_id )
    for t in student_tokens:
        r = answer_quiz_for_student( t, course.id, quiz_id, question_ids )
        answers.append( r )
    return answers
