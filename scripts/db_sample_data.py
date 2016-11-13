from app.models import *
from app import db

# Delete existing data ----------------
with db.session.no_autoflush:
    for user in User.query.all():
        db.session.delete(user)

    for role in Role.query.all():
        db.session.delete(role)

    for request in Request.query.all():
        db.session.delete(request)

    # Commit changes
    db.session.commit()

    # Create some test users -------
    user1 = User(604048, "Shawn McCarthy")
    user2 = User(604049, "Steve Vingerhoet", 604048)
    db.session.add_all([user1, user2,
                        User(604050, "Jacob Taylor", 604049),
                        User(604051, "Regan Yee", 604049),
                        User(604052, "Random Guy", 604048, "tester", False),
                        User(604053, "Some Intern", 604051)])
    # Create some test roles -------
    role1 = Role("UPS User", "UPS Access")
    role2 = Role("UPS Role Create", "UPS Role Creation Access")
    role3 = Role("UPS Maintenance", "UPS Admin Read Access")
    role4 = Role("UPS Admin", "UPS Admin Access")
    role5 = Role("My Role 1", "Child UPS Role")
    role6 = Role("My Role 2", "Child UPS Admin Role")
    db.session.add_all([role1, role2, role3, role4, role5, role6,
                        Role("Test Role 1", "Where am I"),
                        Role("Test Role 2", "Whats happening"),
                        Role("Test Role 3", "Test"),
                        Role("Test Role 4", "Test"),
                        Role("Test Role 5", "Testing123")])
    # Commit changes
    db.session.commit()
    # Create some test Requests -------
    db.session.add_all([Request(4, 604048, 604048, "TestComment", "REVOKED"),
                        Request(3, 604049, 604048, "TestComment", "APPROVED"),
                        Request(2, 604050, 604049, "TestComment", "PENDING"),
                        Request(3, 604051, 604050, "TestComment", "REJECTED")])
    # Create some test Role Approvers
    role1.add_approvers([user1, user2])
    db.session.commit()

# Prove that changes were made
print("Users: " + str(User.query.all()))
print("Roles: " + str(Role.query.all()))
print("Requests: " + str(Request.query.all()))
