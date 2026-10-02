from models.departments import Department

class DepartmentRepository:
    def __init__(self, session):
        self.session = session

    def get_department_by_id(self, department_id):
        return self.session.query(Department).filter(Department.id == department_id).first()

    def create_department(self, name):
        new_department = Department(name=name)
        self.session.add(new_department)
        self.session.commit()
        return new_department

    def update_department(self, department_id, name=None):
        department = self.get_department_by_id(department_id)
        if not department:
            return None
        if name is not None:
            department.name = name
        self.session.commit()
        return department

    def delete_department(self, department_id):
        department = self.get_department_by_id(department_id)
        if not department:
            return None
        self.session.delete(department)
        self.session.commit()
        return department
    def get_all_departments(self):
        return self.session.query(Department).order_by(Department.name).all()