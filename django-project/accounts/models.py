import decimal

from django.db import models
from django.contrib.auth.models import User

from dishes.models import Order, DishPost, DishRequest

class CreateAccountRequest(models.Model):
    """
    Django class representing a Create Account Request.

    Attributes:

    user:
        The User object created as a result of this request being approved.

    username:
        The username for the account, if it is created.

    first name:
        The first name of the person applying for an NGS account.

    last name:
        The last name of the person applying for an NGS account.

    email:
        The email the person wishes to associate with this account. The email
        must be unique

    latitude:
        The default latitude coordinate for this account.

    longitude:
        The default longitude coordinates for this account.

    status:
        The status of this account. Status descriptions are given below.

        pending:
            A system administrator has yet to review this request and take an
            action on it.
        approved:
            A system administrator has approved this request.
        rejected:
            A system administrator has rejected this request.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    latitude = models.DecimalField(max_digits=9,
                                   decimal_places=6,
                                   default=decimal.Decimal(0.0))
    longitude = models.DecimalField(max_digits=9,
                                    decimal_places=6,
                                    default=decimal.Decimal(0.0))

    PENDING, APPROVED, REJECTED = 0, 1, 2

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)



class TerminateAccountRequest(models.Model):
    """
    Django class representing a Terminate Account Request.

    Attributes:

    user:
        The user who has requested that their account be terminated.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class ChefPermissionsRequest(models.Model):
    """
    Django class representing a chef permissions request.

    Attributes:

    user:
    first_dish_name:
    first_dish_image:
    second_dish_name:
    second_dish_image:
    third_dish_name:
    third_dish_image:
    video_biography:

    status:
        The status of this account. Status descriptions are given below.

        pending:
            A system administrator has yet to review this request and take an
            action on it.
        approved:
            A system administrator has approved this request.
        rejected:
            A system administrator has rejected this request.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    first_dish_name = models.CharField(max_length=256)
    first_dish_image = models.ImageField(
        max_length=256,
        upload_to="chef-permissions-requests-uploads/"
    )

    second_dish_name = models.CharField(max_length=256)
    second_dish_image = models.ImageField(
        max_length=256,
        upload_to="chef-permissions-requests-uploads/"
    )

    third_dish_name = models.CharField(max_length=256)
    third_dish_image = models.ImageField(
        max_length=256,
        upload_to="chef-permissions-requests-uploads/"
    )

    video_biography = models.FileField(
        max_length=256,
        upload_to="chef-permissions-requests-uploads/"
    )

    PENDING, APPROVED, REJECTED = 0, 1, 2

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

class Suggestion(models.Model):
    """
    Django class representing a suggestion made by a visitor or user to the
    site.

    Attributes:

    suggestion:
        The suggestion being made by the visitor or user.
    """
    suggestion = models.TextField()

class RedFlag(models.Model):
    """
    Django class representing a red flag that is raised on a user.

    Attributes:

    user:
        The user who is flagged by this RedFlag instance.

    reason:
        The coded reason why the user has been flagged. Code descriptions are
        below.

        Critical:
            This user has been flagged because they have met the criteria of
            giving 3 lowest ratings and 3 complaints.

        Generous:
            This user has been flagged because they have given 5 highest
            ratings for the last 5 transactions.

    status:
        The status of this RedFlag. Status descriptions are below.

        Pending:
            A superuser has not yet decided how to resolve this RedFlag.
        Closed:
            A superuser has reviewed this RedFlag and the issue has been
            closed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    CRITICAL, GENEROUS = range(2)

    REASON_CHOICES = (
        (CRITICAL, "User has given 3 lowest ratings and 3 complaints."),
        (GENEROUS, ("User has given 5 highest ratings "
                   "in the last 5 transactions."))
    )

    reason = models.IntegerField(choices=REASON_CHOICES)

    PENDING, CLOSED = range(2)

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (CLOSED, "Closed")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

class Complaint(models.Model):
    """
    Django class representing a complaint made by one user against another.

    Attributes:

    complainant:
        The user making the complaint against the complainee.

    complainee:
        The user the complaint is being made against.

    description:
        A description of the complaint the complainant is making.

    struck:
        Whether the complainant has been suspended as a result of making
        this complaint.

    status:
        The status of this complaint. Status descriptions are given below.

        Pending:
            A superuser has not yet decided how to resolve this Complaint.
        Closed:
            A superuser has reviewed this Complaint and the issue has been
            closed.
    """
    complainant = models.ForeignKey(User,
                                    on_delete=models.CASCADE,
                                    related_name="complaint_allegations")
    complainee = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   related_name="complaint_receipts")
    description = models.TextField("Complaint Description")
    struck = models.BooleanField(default=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    PENDING, CLOSED = 0, 1

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (CLOSED, "Closed")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

class SuspensionInfo(models.Model):
    """
    Django class representing the number of times a user has been suspended.

    Attributes:

    user:
        The user with which this SuspensionCount is associated.

    count:
        The number of times the user has been suspended.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    suspended = models.BooleanField(default=False)
    count = models.IntegerField(default=0)

    def suspend(self):
        self.suspended = True
        self.count = self.count + 1
        self.save()

class Balance(models.Model):
    """
    Django class representing the balance a user has on their account.

    Attributes:

    user:
        The user with which this Balance is associated.

    amount:
        The amount of the user's balance.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11,
                                 decimal_places=6,
                                 default=decimal.Decimal(0.0))
    is_vip = models.BooleanField(default=False)

    def credit(self, amt):
        self.amount = self.amount + amt
        self.update_vip_status()

    def debit(self, amt):
        self.amount = self.amount - amt
        self.update_vip_status()

    VIP_THRESHOLD = decimal.Decimal(5000)

    def update_vip_status(self):
        self.is_vip = self.amount > Balance.VIP_THRESHOLD
        ntransactions = 0
        diner = self.user.diner
        orders = diner.order_set.filter(status=Order.COMPLETE)
        dishrequests = diner.dishrequest_set.filter(status=DishRequest.COMPLETE)
        ntransactions += orders.count()
        ntransactions += dishrequests.count()
        if hasattr(self.user, "chef"):
            dishposts = self.user.chef.dishpost_set.filter(status=DishPost.COMPLETE)
            ntransactions += dishposts.count()
        if ntransactions > 5:
            self.is_vip = hasattr(self.user, "complaint_receipts")
        self.save()

    def has_funds(self, amt):
        return self.amount >= amt

class RemoveSuspensionRequest(models.Model):
    """
    Django class representing a request to remove a suspension.

    Attributes:

    user:
        The user that is requesting to have the suspension on her account
        removed.

    justification:
        An justification for removing the suspension on the user's account.
        For example "Mea culpa, I've learned my lesson."

    status:
        The status of the Remove Suspension Request. Status descriptions are
        below.

        PENDING:
            A superuser has not yet made a decision on the request.
        APPROVED:
            A superuser has reviewed and approved the request.
        DENIED:
            A superuser has reviewed and denied the request.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    justification = models.TextField()

    PENDING, APPROVED, DENIED = range(3)

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (DENIED, "Denied")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
