from backend.Repositories.department_repository import DepartmentRepository


class DepartmentService:
    def __init__(self, session):
        self.session = session
        self.department_repository = DepartmentRepository(session)

    def get_department_by_id(self, department_id):
        return self.department_repository.get_department_by_id(department_id)

    def get_all_departments(self):
        return self.department_repository.get_all_departments()

    def create_department(self, name):
        return self.department_repository.create_department(name)
