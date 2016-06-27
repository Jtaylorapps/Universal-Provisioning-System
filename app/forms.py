from flask.ext.login import login_user
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SubmitField, PasswordField, SelectField, TextAreaField, \
    SelectMultipleField
from wtforms.validators import InputRequired, ValidationError
from app.models import *


# Create a new type of select field that supports dynamic choices added by the browser
class DynamicSelectField(SelectField):
    # Pass pre-validation to prevent 'invalid choice' error
    def pre_validate(self, form):
        pass


# Create a new type of multiple select field that supports dynamic choices added by the browser
class DynamicSelectMultipleField(SelectMultipleField):
    # Pass pre-validation to prevent 'invalid choice' error
    def pre_validate(self, form):
        pass


# Verify that the login information entered does exist
def validate_login(form, field):
    # Parse the form
    user_id = form.username.data
    password = str(form.password.data)
    remember_me = bool(form.remember_me.data)

    # Verify the user ID is formatted correctly
    if len(user_id) == 6 and user_id.isdigit():
        user_id = int(user_id)
        # Find a user within the database with matching user ID
        user = User.query.get(user_id)
        # Validate login information
        if user is not None and user.password == password:
            # User ID and password match, log the user in
            login_user(user, remember=remember_me)
        else:
            # Throw this if the login information entered is incorrect
            raise ValidationError('Invalid login information.')
    else:
        # Throw this if the user ID is formatted incorrectly
        raise ValidationError('User ID formatted incorrectly.')


# Verify that the Role name does not already exist
def validate_role_name(form, field):
    # Get the Role represented by the given name
    if Role.get_by_name(str(form.name.data)) is not None:
        # Throw this if we don't have a valid user in the DB
        raise ValidationError('A role with that name already exists.')


# Verify that no children are added to a permission and that the children and parents list are mutually exclusive
def validate_role_inheritance(form, field):
    children = form.children.data
    parents = form.parents.data
    if form.type.data == 'PERMISSION' and children is not None:
        # Throw this if a child role is attempted to be added to a Permission
        raise ValidationError('Unable to add a child to a Permission.')
    if any(x in parents for x in children):
        # Throw this if a Role is in both the Parent and Children dropdown
        raise ValidationError('Unable to add a Role as both a parent and child.')


# Login form
class LoginForm(Form):
    # Username field. Must have input and fit the correct formatting requirements
    username = StringField(label='Username', id='TXT_Username', validators=[InputRequired()])
    # Password field. Must have input.
    password = PasswordField(label='Password', id='TXT_Password', validators=[InputRequired()])
    # Remember Me checkbox.
    remember_me = BooleanField(label='Remember Me', id='CHK_Remember_Me', default=True)
    # Submit button for the form
    submit = SubmitField(label='Sign In', id='BTN_Submit', validators=[validate_login])


# User search form
class SearchForm(Form):
    # Search textfield
    query = StringField(label='Search', id='TXT_Search', validators=[InputRequired()])
    # Search button
    submit = SubmitField(label='Search', id='BTN_Submit')


# Role Create form
class RoleCreateForm(Form):
    # Name text field
    name = StringField(label='Role Name', id='TXT_Name', validators=[InputRequired()])
    # Description text area
    desc = TextAreaField(label='Role Description', id='TXT_Desc')
    # Type select field
    type = SelectField(label='Role Type', id="DRP_Type",
                       choices=[('PERMISSION', 'PERMISSION'),
                                ('APPLICATION', 'APPLICATION'),
                                ('FUNCTIONAL', 'FUNCTIONAL')],
                       default='PERMISSION', validators=[InputRequired()])
    # Approvers select field
    approvers = DynamicSelectMultipleField(label='Add Approvers', id='DRP_Approvers', choices=[], coerce=int)
    # Parent select field
    parents = DynamicSelectMultipleField(label='Add Parents', id='DRP_Parents', choices=[], coerce=int)
    # Children select field
    children = DynamicSelectMultipleField(label='Add Children', id='DRP_Children', choices=[], coerce=int)
    # Submit button button
    submit = SubmitField(label='Submit', id='BTN_Submit', validators=[validate_role_name, validate_role_inheritance])


# Assign Access form
class AssignAccessForm(Form):
    # Users select field
    users = DynamicSelectMultipleField(label='Select Users', id='DRP_User',
                                       choices=[], coerce=int,
                                       validators=[InputRequired()])
    # Roles select field
    roles = DynamicSelectMultipleField(label='Select Roles', id='DRP_Role',
                                       choices=[], coerce=int,
                                       validators=[InputRequired()])
    # Comment text area
    comment = TextAreaField(label='Comment', id='TXT_Comment')
    # Submit button button
    submit = SubmitField(label='Assign', id='BTN_Submit')
