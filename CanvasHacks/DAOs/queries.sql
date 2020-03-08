-- noinspection SqlNoDataSourceInspectionForFile



SELECT s.name AS student, s.id AS canvas_id, s.csun_id,
sring.name AS reviewing,
inv.sent_at AS invited_to_review,
sby.name AS reviewed_by
from students s
-- person they are reviewing
INNER JOIN students sring ON rass.assessee_id = sring.id
INNER JOIN review_associations rass ON s.id = rass.assessor_id
-- person they are reviewed by
INNER JOIN students sby ON revby.assessor_id = sby.id
INNER JOIN review_associations revby ON s.id = revby.assessee_id
-- when they were invited to the the review
LEFT JOIN invitation_received inv ON s.id = inv.student_id AND inv.activity_id = rass.activity_id
LEFT JOIN feedback_received fb ON s.id = fb.student_id AND fb.activity_id = rass.activity_id
WHERE rass.activity_id = 638259
AND revby.activity_id = 638259
