"""
Created by adam on 2/18/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass

REVIEW_NOTICE_TEMPLATE = """
    Hi {name},
    
    {intro}
    =======================
    
    {responses}
    
    =======================
    {other}
    
     Please make sure you read the instructions in {review_assignment_name} before getting started.
     
     To complete your review, open the quiz named 
             {review_assignment_name} 
             {review_url}
    {access_code_message}
    
    As always, canvas will lie to you about time limits by displaying an ominous, but meaningless in this course, 'Time Elapsed' timer. There is no time-limit other than you must submit your review before 11.59PM on {due_date}. 
    
    You may open and look at the peer review assignment as many times as you like.
    
    Please remember that the person you are reviewing is not the person reviewing you.
        
    Enjoy,
    /a
   
    """

# Used to notify the author that it is time to do the metareview
METAREVIEW_NOTICE_TEMPLATE = """
    Hi {name},
    
    The peer-review responses from the student who read your work are below. Please read them carefully and re-read your original assignment. Then follow the instructions at the bottom of this message to give the reviewer feedback on their review :
    =======================
    
    {responses}
    
    =======================
    {other}
    
    Personally, whenever I get critical feedback on something I've written, my first impression is always wrong ---I either think the problems mentioned are more trivial than they are or go in the opposite direction and overinflate every minor thing into something huge. Thus it may be a good idea to take a break before completing the metareview. 
    
    Please remember that the person who reviewed you is not the person you reviewed.
    
    When you're ready to complete the metareview and give the reviewer feedback, please make sure you read the instructions in {review_assignment_name} before getting started.
     
     To complete your review of their review, open the quiz named 
             {review_assignment_name} 
             {review_url}
     {access_code_message}
    
    As always, canvas will lie to you about time limits by displaying an ominous, but meaningless in this course, 'Time Elapsed' timer. There is no time-limit other than you must submit your review before 11.59PM on {due_date}. 
    
    You may open and look at the metareview assignment as many times as you like.
        
    Enjoy,
    /a
    
    PS, Please let me know if anything seems strange about the review I've sent you. I've tested my software as best I can, but....
   
    """

# Used to send metareview responsese by author to reviewer
METAREVIEW_CONTENT_TEMPLATE = """
 Hi {name},
    
    {intro}
    =======================
    
    {responses}
    
    =======================
    {other}
    
    
    All best wishes,
    /a
   

"""

DISCUSSION_REVIEW_NOTICE_TEMPLATE = """
    Hi {name},
    
    {intro}
    =======================
    
    {responses}
    
    =======================
    {other}
    
     Please make sure you read the instructions in {review_assignment_name} before getting started.
     
     To complete your review, open the assignment named 
             {review_assignment_name} 
             {review_url}
    {access_code_message}
    
    As always, canvas will lie to you about time limits by displaying an ominous, but meaningless in this course, 'Time Elapsed' timer. There is no time-limit other than you must submit your review before 11.59PM on {due_date}. 
    
    You may open and look at the review assignment as many times as you like.
    
    Please remember that the person you are reviewing is not the person reviewing you.
        
    Enjoy,
    /a
   """

# Sending the results of the discussion review to the students
DISCUSSION_REVIEW_FEEDBACK_TEMPLATE = """
Hi {name},
    
    {intro}
    =======================
    
    {responses}
    
    =======================
    {other}
    
    I hope you find this useful. If they have made points with which you disagree, read over your posts and practice trying to see what they had in mind. You might still disagree. But please remember the secondary goal of this is to learn to see your own work through someone else's eyes. That skill is incredibly important, rare, and difficult to learn; it will help you in any industry. So please seize every opportunity for practice. 
    
    All best wishes,
    /a
   
"""