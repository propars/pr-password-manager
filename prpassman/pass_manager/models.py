from django.db import models


class NonArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class Password(models.Model):
    name = models.CharField(max_length=255)
    hash = models.CharField(max_length=100)
    creation_time = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField()
    is_alive = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    objects = NonArchivedManager()

    def __str__(self):
        return self.name


class ArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=True)


class ArchivedPassword(Password):
    objects = ArchivedManager()

    class Meta:
        proxy = True

