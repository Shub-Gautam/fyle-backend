from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, GradeEnum
from flask import jsonify, make_response

from .schema import AssignmentSchema, AssignmentGradeSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    teachers_assignments = Assignment.get_assignments_by_teacher_filter(p.teacher_id)

    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    submitted_graded_assignments = [a for a in teachers_assignments if a.state != 'DRAFT']
    teachers_assignments_dump = AssignmentSchema().dump(submitted_graded_assignments, many=True)
    if submitted_graded_assignments:
        teachers_assignments_dump = AssignmentSchema().dump(submitted_graded_assignments, many=True)
        return APIResponse.respond(data=teachers_assignments_dump)
    # return APIResponse.respond(data=teachers_assignments_dump)


@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    get_assignment = Assignment.get_assignment_by_id(grade_assignment_payload.id)
    # if grade_assignment_payload.grade not in
    assert grade_assignment_payload.grade in GradeEnum.__members__.values()
    if not get_assignment:
        return make_response(jsonify(error='FyleError'), 404)
    if get_assignment.teacher_id == p.teacher_id and get_assignment.state == 'SUBMITTED':
        graded_assignment = Assignment.mark_grade(
            _id=grade_assignment_payload.id,
            grade=grade_assignment_payload.grade,
            auth_principal=p
        )
        db.session.commit()
        graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
        return APIResponse.respond(data=graded_assignment_dump)
    else:
        return make_response(jsonify(error="FyleError"), 400)



    # graded_assignment = Assignment.mark_grade(
    #     _id=grade_assignment_payload.id,
    #     grade=grade_assignment_payload.grade,
    #     auth_principal=p
    # )
    # db.session.commit()
    # graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    # return APIResponse.respond(data=graded_assignment_dump)
