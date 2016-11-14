import json

from flask import render_template, redirect, abort, url_for, request, g
from flask.ext.login import logout_user, current_user, login_required

from app import app, lm
from config import *
from .forms import *
from .models import *


# Set up our global user variable
@app.before_request
def before_request():
    g.user = current_user


# Loads a user from the database. Used by Flask-Login.
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


# Handle the login page
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Check if g.user is set to an authenticated user
    if g.user is not None and g.user.is_authenticated:
        # Redirect to the index page
        return redirect(url_for('index'))

    # Create login form
    form = LoginForm()

    if form.submit.data and form.validate_on_submit():
        # Redirect to the index or the next page
        return redirect(request.args.get('next') or url_for('index'))
    else:
        # If the user has not logged in, send to the login page
        return render_template('login.html', form=form)


# Handle the index page
@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'Approve' in request.form:
            # If an approval was submitted, set approval_status to approved
            g.user.update_approval(int(request.form['Approve']), "APPROVED")
        elif 'Reject' in request.form:
            # If a rejection was submitted, set approval_status to rejected
            g.user.update_approval(int(request.form['Reject']), "REJECTED")
    # Get first five active incoming Requests for the current User
    incoming = g.user.active_approvals.limit(5).all()
    # Get first five outgoing Requests for the current User
    outgoing = g.user.requests_by.limit(5).all()
    return render_template('index.html', incoming=incoming, outgoing=outgoing)


# Handle all of the user pages
@app.route('/user/<int:user_id>/')
@app.route('/user/<int:user_id>/<subpage>/')
@login_required
def user_page(user_id, subpage=''):
    # Find the User or throw a 404 if they do not exist
    user = User.query.get_or_404(user_id)

    if subpage == 'roles':
        # Visit the user's active roles page
        data = user.active_roles.all()
        headers = ["Name", "Description"]
        return render_template('user_roles.html', headers=headers, data=data, user=user)
    elif subpage == 'requests':
        # Visit the user's active roles page
        data = user.requests_by.all()
        headers = ["Status", "Role", "Requested For", "Comment"]
        return render_template('user_requests.html', headers=headers, data=data, user=user)
    elif subpage == '':
        # Load the default user page
        return render_template('user.html', user=user)
    else:
        # Trying to visit an invalid user page, throw 404
        abort('404')


# Handle all of the user pages
@app.route('/role/<int:role_id>/')
@login_required
def role_page(role_id):
    # Find the Role or throw a 404 if it doesn't exist
    role = Role.query.get_or_404(role_id)
    # Render the user page with the given role
    return render_template('role.html', role=role)


# Handle the Browse page
@app.route('/browse/<type>/<int:page_num>/', methods=['GET', 'POST'])
@app.route('/browse/<type>/', methods=['GET', 'POST'])
@login_required
def browse(type, page_num=1):
    form = SearchForm()
    if type.lower() == 'users' or type.lower() == 'user':
        # Search User Page
        page = "browse_users.html"
        # Create column headers
        headers = ["Emp ID", "Name", "Manager"]

        if form.submit.data and form.validate_on_submit():
            # Search the id and name column
            data = User.search(form.query.data)
            page_num = 1
        else:
            # Render the full set of users as no search query was provided
            data = User.query
    elif type.lower() == 'roles' or type.lower() == 'role':
        # Search Role Page
        page = "browse_roles.html"
        # Create column headers
        headers = ["Name", "Description"]

        if form.submit.data and form.validate_on_submit():
            # Search the role name column
            data = Role.search(form.query.data)
            page_num = 1
        else:
            # Render the full set of roles as no search query was provided
            data = Role.query
    elif type.lower() == 'requests' or type.lower() == 'request':
        # Search Request Page
        page = "browse_requests.html"
        # Create column headers
        headers = ["Status", "Role", "Requested For", "Requested By", "Comment"]

        if form.submit.data and form.validate_on_submit():
            # Search by role name or requestor name/id
            data = Request.search(form.query.data)
            page_num = 1
        else:
            # Render the full set of roles as no search query was provided
            data = Request.query
    else:
        # Invalid request, send to error page
        abort(404)
    # Handle pagination
    data = data.paginate(page_num, RESULTS_PER_PAGE, True)
    # Request the page
    return render_template(page, form=form, headers=headers, data=data, type=type)


# Handle the Role Create page
@app.route('/rolecreate/', methods=['GET', 'POST'])
@login_required
def create_role():
    form = RoleCreateForm()
    if form.submit.data and form.validate_on_submit():
        # Create the new Role object
        new_role = Role(form.name.data, form.desc.data)
        # Add specified Approvers to the new Role
        new_role.add_approvers(form.approvers.data)
        # Add specified Parents to the new Role
        new_role.add_parents(form.parents.data)
        # Add specified Children to the new Role
        new_role.add_children(form.children.data)
        # Add the new Role to the database
        db.session.add(new_role)
        # Commit the new role to the database
        db.session.commit()
        # Redirect back to the page
        return redirect(url_for('role_page', role_id=new_role.id))
    return render_template('create_role.html', form=form)


# Handle the Assign Access page
@app.route('/assign/', methods=['GET', 'POST'])
@login_required
def assign():
    form = AssignAccessForm()
    if form.submit.data and form.validate_on_submit():
        # Create a new Request and add it to the database for each Role assigned to each User
        for user in form.users.data:
            for role in form.roles.data:
                # If there is not an existing, identical, and active Request, create a new one
                if Request.get_active_request(role, user) is None:
                    # Add the new Request to the database
                    db.session.add(Request(role, user, g.user.id, form.comment.data))
                    # Save database changes
                    db.session.commit()
        # Redirect back to the page
        return redirect(url_for('assign'))
    return render_template('assign_access.html', form=form)


# Handle requests to look up a User
@app.route("/finduser/", methods=['GET'])
def find_user():
    # Search for the User with the given query
    users = User.search(request.args.get('user')).all()
    # Results found, get needed information
    results = []
    for user in users:
        # Make a list in the form (id, text) for Select2 to parse
        results.append({"id": user.id, "text": user.name + " (" + str(user.id) + ")"})
    # Convert the first five results to JSON
    return json.dumps(results[:5])


# Handle requests to look up a Role
@app.route("/findrole/", methods=['GET'])
def find_role():
    # Search for the Role with the given query
    roles = Role.search(request.args.get('role')).all()
    # Results found, get needed information
    results = []
    for role in roles:
        # Make a list in the form (id, text) for Select2 to parse
        results.append({"id": role.id, "text": role.name})
    # Convert the first ten results to JSON
    return json.dumps(results[:10])


@app.route("/logout/")
@login_required
def logout():
    # Log the user out
    logout_user()
    # Redirect back to the login page
    return redirect(url_for('login'))


# Handle any 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
