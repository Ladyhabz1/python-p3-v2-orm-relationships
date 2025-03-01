import sqlite3

# Establish database connection
CONN = sqlite3.connect('company.db')
CURSOR = CONN.cursor()

class Employee:
    all = {}  # Dictionary of objects saved to the database

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Dept {self.department_id}>"

    @classmethod
    def create_table(cls):
        """Creates the employees table if it doesn't exist."""
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE CASCADE
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drops the employees table."""
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()

    def save(self):
        """Inserts or updates an employee record in the database."""
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)",
                (self.name, self.job_title, self.department_id)
            )
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, name, job_title, department_id):
        """Creates an employee, saves it to the database, and returns the instance."""
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def update(self):
        """Updates an existing employee's information in the database."""
        if self.id:
            CURSOR.execute(
                "UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?",
                (self.name, self.job_title, self.department_id, self.id)
            )
            CONN.commit()

    def delete(self):
        """Deletes the employee from the database."""
        if self.id:
            CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
            CONN.commit()
            Employee.all.pop(self.id, None)
            self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Creates an Employee instance from a database row."""
        if row is None:
            return None
        employee = cls.all.get(row[0])
        if employee:
            employee.name = row[1]
            employee.job_title = row[2]
            employee.department_id = row[3]
        else:
            employee = cls(row[1], row[2], row[3], id=row[0])
            cls.all[row[0]] = employee
        return employee

    @classmethod
    def get_all(cls):
        """Returns a list of all Employee instances from the database."""
        CURSOR.execute("SELECT * FROM employees")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_name(cls, name):
        """Finds an employee by name and returns an instance."""
        CURSOR.execute("SELECT * FROM employees WHERE name = ?", (name,))
        return cls.instance_from_db(CURSOR.fetchone())

    @classmethod
    def find_by_id(cls, id):
        """Finds an employee by ID and returns an instance."""
        CURSOR.execute("SELECT * FROM employees WHERE id = ?", (id,))
        return cls.instance_from_db(CURSOR.fetchone())
