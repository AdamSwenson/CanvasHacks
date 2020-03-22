"""
Logging and reporting penalties

Created by adam on 3/18/20
"""
__author__ = 'adam'

if __name__ == '__main__':
    pass


class PenaltyLogger:

    @staticmethod
    def log(  penalizer ):
        if len( penalizer.penalty_messages ) > 0:
            for msg in penalizer.penalty_messages:
                print(msg)


            # for penalty_dict in penalizer.penalized_records:
            #     due_at = None
            #     try:
            #         due_at = penalizer.due_date
            #     except AttributeError:
            #         # Some penalizers may not have a due date
            #         pass
            #     msg = self._penalty_message( penalty_dict[ 'penalty' ], penalty_dict[ 'record' ], due_at=None )
            #     print(msg)


    # def _penalty_message( self, penalty, row, due_at=None ):
    #     """
    #     Handles printing or logging of penalties applied
    #
    #     # todo enable logging
    #
    #     :param penalty:
    #     :param row:
    #     :return:
    #     """
    #     stem = 'Student #{}: Submitted on {}; was due {}. Penalized {}'
    #     return stem.format( row[ 'student_id' ], row[ 'submitted' ], due_at, penalty )

