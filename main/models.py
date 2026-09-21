import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import Now


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(db_default=Now(), editable=False)
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        abstract = True


class AgeRating(models.IntegerChoices):
    ZERO = 0, "0+"
    SIX = 6, "6+"
    TWELVE = 12, "12+"
    SIXTEEN = 16, "16+"
    EIGHTEEN = 18, "18+"


class Film(TimestampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(default="", blank=True)
    duration_minutes = models.PositiveSmallIntegerField()
    age_rating = models.PositiveSmallIntegerField(choices=AgeRating.choices)
    release_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=2, default="", blank=True)
    director = models.CharField(max_length=255, default="", blank=True)
    is_active = models.BooleanField(default=True, db_default=True)

    genres = models.ManyToManyField(
        "Genre",
        related_name="films",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(duration_minutes__gt=0),
                name="films_duration_minutes_positive",
            ),
            models.CheckConstraint(
                condition=Q(age_rating__in=AgeRating.values),
                name="films_age_rating_valid",
            ),
        ]

    def __str__(self):
        return self.title


class Customer(TimestampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.full_name


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Hall(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(default="", blank=True)
    is_active = models.BooleanField(default=True, db_default=True)

    def __str__(self):
        return self.name


class Seat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hall = models.ForeignKey(
        "Hall",
        on_delete=models.CASCADE,
        related_name="seats",
        db_index=False,
    )
    row_number = models.PositiveSmallIntegerField()
    seat_number = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hall", "row_number", "seat_number"],
                name="seats_hall_row_seat_uniq",
            ),
            models.CheckConstraint(
                condition=Q(row_number__gt=0),
                name="seats_row_number_positive",
            ),
            models.CheckConstraint(
                condition=Q(seat_number__gt=0),
                name="seats_seat_number_positive",
            ),
        ]
        ordering = ["row_number", "seat_number"]

    def __str__(self):
        return f"Ряд {self.row_number}, место {self.seat_number}"


class SessionStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Запланирован"
    CANCELLED = "cancelled", "Отменён"
    FINISHED = "finished", "Завершён"


class Session(TimestampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film = models.ForeignKey(
        "Film",
        on_delete=models.RESTRICT,
        related_name="sessions",
    )
    hall = models.ForeignKey(
        "Hall",
        on_delete=models.RESTRICT,
        related_name="sessions",
        db_index=False,
    )
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.SCHEDULED,
        db_default=SessionStatus.SCHEDULED,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="sessions_price_non_negative",
            ),
        ]
        indexes = [
            models.Index(
                fields=["hall", "start_time"],
                name="ix_sessions_hall_start_time",
            ),
        ]

    def __str__(self):
        return f"{self.film} — {self.start_time:%d.%m.%Y %H:%M}"


class TicketStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        "Session",
        on_delete=models.RESTRICT,
        related_name="tickets",
        db_index=False,
    )
    seat = models.ForeignKey(
        "Seat",
        on_delete=models.RESTRICT,
        related_name="+",
    )
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.SET_NULL,
        related_name="tickets",
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        TicketStatus,
        on_delete=models.RESTRICT,
        related_name="tickets",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(db_default=Now(), db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "seat"],
                name="tickets_session_seat_uniq",
            ),
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="tickets_price_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.session} — {self.seat}"
