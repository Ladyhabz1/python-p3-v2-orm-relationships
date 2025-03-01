from __init__ import CURSOR, CONN

class Department:
    all = {}  # Dictionary of objects saved to the database

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """Creates the departments table if it doesn't exist."""
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drops the departments table."""
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()

    def save(self):
        """Inserts or updates a department record in the database."""
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO departments (name, location) VALUES (?, ?)",
                (self.name, self.location)
            )
            self.id = CURSOR.lastrowid
            Department.all[self.id] = self
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, name, location):
        """Creates a department, saves it to the database, and returns the instance."""
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Updates an existing department's information in the database."""
        if self.id:
            CURSOR.execute(
                "UPDATE departments SET name = ?, location = ? WHERE id = ?",
                (self.name, self.location, self.id)
            )
            CONN.commit()

    def delete(self):
        """Deletes the department from the database."""
        if self.id:
            CURSOR.execute("DELETE FROM departments WHERE id = ?", (self.id,))
            CONN.commit()
            Department.all.pop(self.id, None)
            self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Creates a Department instance from a database row."""
        if row is None:
            return None
        department = cls.all.get(row[0])
        if department:
            department.name = row[1]
            department.location = row[2]
        else:
            department = cls(row[1], row[2], id=row[0])
            cls.all[row[0]] = department
        return department

    @classmethod
    def get_all(cls):
        """Returns a list of all Department instances from the database."""
        CURSOR.execute("SELECT * FROM departments")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Finds a department by ID and returns an instance."""
        CURSOR.execute("SELECT * FROM departments WHERE id = ?", (id,))
        return cls.instance_from_db(CURSOR.fetchone())

    @classmethod
    def find_by_name(cls, name):
        """Finds a department by name and returns an instance."""
        CURSOR.execute("SELECT * FROM departments WHERE name = ?", (name,))
        return cls.instance_from_db(CURSOR.fetchone())

    def employees(self):
        """Returns a list of all employees in the current department."""
        from employee import Employee  # Import inside method to prevent circular import
        CURSOR.execute("SELECT * FROM employees WHERE department_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Employee.instance_from_db(row) for row in rows]
