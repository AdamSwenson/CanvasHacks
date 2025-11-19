import CanvasHacks.testglobals

CanvasHacks.testglobals.TEST = True
CanvasHacks.testglobals.use_api = False

from CanvasHacks.Models.message_queue import MessageQueueItem
from CanvasHacks.Repositories.messaging import MessageRepository
from TestingBase import TestingBase
from factories.ModelFactories import student_factory, message_queue_item_factory
from factories.PeerReviewedFactories import unit_factory
from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.Repositories.status import InvitationStatusRepository, FeedbackStatusRepository


class TestMessageRepository(TestingBase):

    def setUp(self):
        self.config_for_test()
        self.unit = unit_factory()
        self.activity = self.unit.initial_work
        self.activity_id = self.activity.id

        self.dao = SqliteDAO()
        self.session = self.dao.session

        self.obj = MessageRepository( self.dao)


    def test__make_status_repos_entry(self):
        status_repos = [InvitationStatusRepository(self.dao, self.activity),
                        FeedbackStatusRepository(self.dao, self.activity, self.unit.review)]

        result = self.obj._make_status_repos_entry(status_repos)
        self.assertEqual(result[0]['type'], 'InvitationStatusRepository')
        self.assertEqual(result[0]['activity_id'], self.activity.id)

        self.assertEqual(result[1]['type'], 'FeedbackStatusRepository')
        self.assertEqual(result[1]['activity_id'], self.activity.id)
        self.assertEqual(result[1]['review_pairings_activity_id'], self.unit.review.id)


    def test_add_to_queue_w_dict(self):
        student = student_factory()
        subject = self.fake.text()
        body = self.fake.text()

        d = {
            'student_id': student.id,
            'subject': subject,
            'body': body,
        }
        # call
        self.obj.add_to_queue(self.activity, **d)

        # check
        results = self.session.query(MessageQueueItem) \
            .filter(MessageQueueItem.activity_id == self.activity_id) \
            .all()


        self.assertEqual(len(results), 1, "one item in queue")
        self.assertIsInstance( results, list, "returns list")
        self.assertIsInstance(results[0], MessageQueueItem)
        self.assertEqual(results[0].activity_id, self.activity_id, "correct activity id")
        self.assertEqual(results[0].student_id, student.student_id, "correct student id")
        self.assertEqual(results[0].subject, subject, "correct subject")
        self.assertEqual(results[0].body, body, "correct body")


    def test_add_to_queue(self):
        student = student_factory()
        subject = self.fake.text()
        body = self.fake.text()

        # call
        self.obj.add_to_queue(self.activity, student_id=student.student_id, subject=subject, body=body)

        # check
        results = self.session.query(MessageQueueItem) \
            .filter(MessageQueueItem.activity_id == self.activity_id) \
            .all()


        self.assertEqual(len(results), 1, "one item in queue")
        self.assertIsInstance( results, list, "returns list")
        self.assertIsInstance(results[0], MessageQueueItem)
        self.assertEqual(results[0].activity_id, self.activity_id, "correct activity id")
        self.assertEqual(results[0].student_id, student.student_id, "correct student id")
        self.assertEqual(results[0].subject, subject, "correct subject")
        self.assertEqual(results[0].body, body, "correct body")


    def test_remove_from_queue(self):
        # prep
        msgs = [message_queue_item_factory() for i in range(0, 5)]
        [self.session.add(m) for m in msgs]
        self.session.commit()
        msgs = self.session.query(MessageQueueItem).all()
        self.assertEqual(len(msgs), 5)
        to_remove = msgs[0]

        # call
        self.obj.remove_from_queue(to_remove)

        # check
        results = self.session.query(MessageQueueItem).all()
        self.assertEqual(len(results), 4)
        self.assertNotIn(to_remove.id, [i.id for i in results], "Item not in results")


    # def test_message_iterator(self):
    #     self.fail()


    def test_get_message_queue_for_activity(self):
        # prep
        other_msgs = [message_queue_item_factory(activity_id=27) for i in range(0, 5)]
        [self.session.add(m) for m in other_msgs]

        msgs = [message_queue_item_factory(activity_id=self.activity_id) for i in range(0, 5)]
        [self.session.add(m) for m in msgs]
        self.session.commit()

        # call
        results = self.obj.get_message_queue(self.activity_id)

        # check
        self.assertEqual(len(results), 5, "expected result count loaded")
        [self.assertEqual(self.activity_id, r.activity_id, "has expected activity id") for r in results]
        [self.assertNotEqual(27, r.activity_id, "other activity messages not loaded") for r in results]


    def test_get_message_queue_for_all(self):
        # prep
        other_msgs = [message_queue_item_factory(activity_id=27) for i in range(0, 5)]
        [self.session.add(m) for m in other_msgs]

        msgs = [message_queue_item_factory(activity_id=self.activity_id) for i in range(0, 5)]
        [self.session.add(m) for m in msgs]
        self.session.commit()

        # call
        results = self.obj.get_message_queue()

        # check
        self.assertEqual(len(results), 10, "expected result count loaded")

    def test_all_to_send(self):
        other_msgs = [message_queue_item_factory(activity_id=27) for i in range(0, 5)]
        [self.session.add(m) for m in other_msgs]

        for r in self.obj.all_to_send:
            self.assertIsNotNone(r)
            self.assertIsInstance(r, MessageQueueItem)

