from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee, Broker

@receiver(post_save, sender=Employee)
def assign_brokers(sender, instance, created, **kwargs):
    if created:
        # Fetch 10 unassigned brokers
        brokers = Broker.objects.filter(assigned_employee=None)[:10]
        for broker in brokers:
            broker.assigned_employee = instance
            broker.save()
