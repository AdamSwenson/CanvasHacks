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
    and use the access code: 
            {access_code}
    
    As always, canvas will lie to you about time limits by displaying an ominous, but meaningless in this course, 'Time Elapsed' timer. There is no time-limit other than you must submit your review before 11.59PM on {due_date}. 
    
    You may open and look at the peer review assignment as many times as you like.
    
    (Apologies for the terrible formatting of this message, Canvas is being annoying).
    
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
    
    When you're ready to complete the metareview and give the reviewer feedback, please make sure you read the instructions in {review_assignment_name} before getting started.
     
     To complete your review of thier review, open the quiz named 
             {review_assignment_name} 
             {review_url}
    and use the access code: 
            {access_code}
    
    As always, canvas will lie to you about time limits by displaying an ominous, but meaningless in this course, 'Time Elapsed' timer. There is no time-limit other than you must submit your review before 11.59PM on {due_date}. 
    
    You may open and look at the metareview assignment as many times as you like.
    
    (Apologies for the terrible formatting of this message, Canvas is being annoying).
    
    Enjoy,
    /a
   
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