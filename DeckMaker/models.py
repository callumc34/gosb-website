from django.db import models

# Create your models here.

class deck(models.Model):
	class Meta:
		db_table = 'Decks'
	DeckId = models.IntegerField()
	DeckName = models.CharField(max_length=75)
	DeckOwner = models.CharField(max_length=30)
	DeckDate = models.DateField(auto_now=False)

def MaxID():
	maxId = deck.objects.all().aggregate(models.Max("DeckId"))["DeckId__max"]
	if maxId:
		return maxId
	else:
		return 0