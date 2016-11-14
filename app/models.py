from sqlalchemy import ForeignKey, Column, Integer, String, Enum, Boolean, Table, or_, and_, desc
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import PasswordType

from app import db


# USER OBJECT ===
class User(db.Model):
    # Model metadata
    __tablename__ = 'users'

    # Model information
    id = Column(Integer, primary_key=True, autoincrement=False)
    password = Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    name = Column(String(64), index=True, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"))
    active_flag = Column(Boolean, default=True, nullable=False)

    # Method for creating new User objects
    def __init__(self, id, name, manager_id=None, password="test", active_flag=True):
        self.id = id
        self.password = password
        self.name = name
        self.manager_id = manager_id
        self.active_flag = active_flag

    # Return True unless the user should not be allowed to authenticate
    @property
    def is_authenticated(self):
        return True

    # Return True for users unless they are inactive
    @property
    def is_active(self):
        return self.active_flag

    # Return True only for fake users that are not supposed to log in to the system
    @property
    def is_anonymous(self):
        return False

    # Return a unique identifier for the user, in unicode format
    def get_id(self):
        return str(self.id)

    # Search for a User with the given query. Searches the id and name fields
    @staticmethod
    def search(query):
        return User.query.filter(or_(User.id.contains(query), User.name.contains(query)))

    # Update this User's approval status for the given Request
    def update_approval(self, request_id, updated_status="PENDING"):
        db.session.execute(request_approvers.update().
                           where(and_(request_approvers.columns.request_id == request_id,
                                      request_approvers.columns.user_id == self.id)).
                           values(approval_status=updated_status))
        if updated_status == "REJECTED":
            # If a single Approver rejects a Request, set the Request status to REJECTED
            Request.query.get(request_id).update_status(updated_status)
        elif updated_status == "APPROVED":
            # Get number of Approvers who have approved this Request
            approved = len(list(db.session.execute(request_approvers.select().where(
                and_(request_approvers.columns.request_id == request_id,
                     request_approvers.columns.user_id == self.id,
                     request_approvers.columns.approval_status == updated_status)))))
            # Get total number of Approvers for this Request
            total = len(list(db.session.execute(request_approvers.select().
                                                where(and_(request_approvers.columns.request_id == request_id,
                                                           request_approvers.columns.user_id == self.id)))))
            if approved == total:
                # If all Approvers approve a Request, set the Request status to APPROVED
                Request.query.get(request_id).update_status(updated_status)
        db.session.commit()

    # To_String method
    def __repr__(self):
        return str(self.id) + " : " + self.name + " : " + str(self.manager_id)


# ROLE PARENT MANY-TO-MANY MAPPING TABLE ===
role_parents = Table(
    'role_parents',
    db.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('parent_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# ROLE APPROVER MANY-TO-MANY MAPPING TABLE ===
role_approvers = Table(
    'role_approvers',
    db.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


# ROLE OBJECT ===
class Role(db.Model):
    # Model metadata
    __tablename__ = 'roles'

    # Modal information
    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True, unique=True, nullable=False)
    desc = Column(String(255))

    # Method for creating new Role objects
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

    # Add a Role as a Parent to this Role. This automatically adds to the Children set via the relationship
    def add_parent(self, parent):
        if isinstance(parent, int):
            parent = Role.query.get(parent)
        if isinstance(parent, Role):
            self.parents.append(parent)
        else:
            raise TypeError("Invalid parent: " + str(parent))

    # Add multiple Roles as Parents to this Role
    def add_parents(self, parents):
        for parent in parents:
            self.add_parent(parent)

    # Add a Role as a Child to this Role. This automatically adds to the Parent set via the relationship
    def add_child(self, child):
        if isinstance(child, int):
            child = Role.query.get(child)
        if isinstance(child, Role):
            self.children.append(child)
        else:
            raise TypeError("Invalid child: " + str(child))

    # Add multiple Roles as Children to this Role
    def add_children(self, children):
        for child in children:
            self.add_child(child)

    # Add a User as an Approver to this Role. This automatically adds to the approver_for set via the relationship
    def add_approver(self, approver):
        if isinstance(approver, int):
            approver = User.query.get(approver)
        if isinstance(approver, User):
            self.approvers.append(approver)
        else:
            raise TypeError("Invalid approver: " + str(approver))

    # Add multiple Users as Approvers to this Role
    def add_approvers(self, approvers):
        for approver in approvers:
            self.add_approver(approver)

    # Get a Role by its exact name
    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()

    # Search for a Role with the given query. Searches the name field
    @staticmethod
    def search(query):
        return Role.query.filter(Role.name.contains(query))

    # To_String method
    def __repr__(self):
        return str(self.id) + " : " + self.name + " : " + self.desc


# REQUEST APPROVER MANY-TO-MANY MAPPING TABLE ===
request_approvers = Table(
    'request_approvers',
    db.metadata,
    Column('request_id', Integer, ForeignKey('requests.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('approval_status', Enum("PENDING", "REJECTED", "APPROVED"), nullable=False, default="PENDING")
)


# REQUEST OBJECT ===
class Request(db.Model):
    # Modal metadata
    __tablename__ = 'requests'

    # Model information
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    requested_for_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(String(255))
    status = Column(Enum("PENDING", "REJECTED", "APPROVED", "REVOKED"))

    # Method for creating new Request objects
    def __init__(self, role_id, requested_for_id, requested_by_id, comment=None, status="PENDING"):
        self.role_id = role_id
        self.requested_for_id = requested_for_id
        self.requested_by_id = requested_by_id
        self.comment = comment
        self.status = status
        # Get Role approvers
        new_request_approvers = set(Role.query.get(role_id).approvers.all())
        # Get requested_for User manager if not None and add to approvers set
        requested_for_manager = User.query.get(requested_for_id).manager
        if requested_for_manager is not None:
            new_request_approvers.add(requested_for_manager)
        # Add Approvers set as Approvers for this Request
        self.add_approvers(new_request_approvers)

    # Check to see if there is an existing active request for the given User and Role
    @staticmethod
    def get_active_request(role_id, user_id):
        return Request.query.filter(Request.role_id == role_id,
                                    Request.requested_for_id == user_id,
                                    Request.status != 'REJECTED').first()

    # Search for a Request with the given query. Searches requested_for name and ID as well as requested_role name
    @staticmethod
    def search(query):
        return Request.query.join(Request.requested_for_id) \
            .join(Request.requested_role) \
            .filter(or_(User.name.contains(query),
                        User.id.contains(query),
                        Role.name.contains(query)))

    # Add a User as an Approver to this Request. This automatically adds to the approver_for_request back ref
    def add_approver(self, approver):
        if isinstance(approver, int):
            approver = User.query.get(approver)
        if isinstance(approver, User):
            self.approvers.append(approver)
        else:
            raise TypeError("Invalid approver: " + str(approver))

    # Add multiple Users as Approvers to this Request
    def add_approvers(self, approvers):
        for approver in approvers:
            self.add_approver(approver)

    # Update the status of the Request
    def update_status(self, updated_status="PENDING"):
        self.status = updated_status

    # To_String method
    def __repr__(self):
        return str(self.id) + " : " + str(self.role_id) + " : " + str(self.requested_for_id) + " : " + self.status


# OBJECT RELATIONSHIPS ===

# Define relationship between a Role and Requests for this Role
Role.requests = relationship('Request', backref='requested_role', lazy='dynamic')
# Define relationship between a Role and its Parents
Role.parents = relationship(
    'Role',  # Specify the table we're forming a relationship with
    secondary=role_parents,  # Specify the mapping table
    primaryjoin=(Role.id == role_parents.c.role_id),  # The primary mapping
    secondaryjoin=(Role.id == role_parents.c.parent_id),  # The secondary mapping
    backref=backref('children', lazy='dynamic'),
    lazy='dynamic'
)
# Define relationship between a Role and its Approvers
Role.approvers = relationship(
    'User',  # Specify the table we're forming a relationship with
    secondary=role_approvers,  # Specify the mapping table
    primaryjoin=(Role.id == role_approvers.c.role_id),  # The primary mapping
    secondaryjoin=(User.id == role_approvers.c.user_id),  # The secondary mapping
    backref=backref('approver_for', lazy='dynamic'),
    lazy='dynamic'
)
# Define relationship between a Request and its Approvers
Request.approvers = relationship(
    'User',  # Specify the table we're forming a relationship with
    secondary=request_approvers,  # Specify the mapping table
    primaryjoin=(Request.id == request_approvers.c.request_id),  # The primary mapping
    secondaryjoin=(User.id == request_approvers.c.user_id),  # The secondary mapping
    backref=backref('approver_for_requests', lazy='dynamic'),
    lazy='dynamic'
)
# Define relationship between a User and Approvals pending their action
Request.pending_approvals = relationship(
    'User',  # Specify the table we're forming a relationship with
    secondary=request_approvers,  # Specify the mapping table
    primaryjoin=and_(Request.id == request_approvers.c.request_id,
                     request_approvers.c.approval_status == 'PENDING',
                     Request.status == 'PENDING'),  # The primary mapping
    secondaryjoin=(User.id == request_approvers.c.user_id),  # The secondary mapping
    backref=backref('active_approvals', lazy='dynamic'),
    lazy='dynamic'
)

# Define relationship between a User and Requests made for them
User.requests_for = relationship('Request', backref='requested_for',
                                 lazy='dynamic', foreign_keys=[Request.requested_for_id])
# Define relationship between a User and Requests that they have made. Sorted from newest Request to oldest.
User.requests_by = relationship('Request', backref='requested_by',
                                lazy='dynamic', foreign_keys=[Request.requested_by_id], order_by=desc(Request.id))
# Define relationship between a User and their Active Roles
User.active_roles = relationship('Request', lazy='dynamic',
                                 primaryjoin=and_(User.id == Request.requested_for_id, Request.status == 'APPROVED'))
# Define relationship between a User and their Manager. Note: Must be declared outside of the class.
User.manager = relationship('User', backref='subordinates', remote_side=User.id, post_update=True)
