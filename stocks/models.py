from django.db import models

# Since we're using MongoDB for main data storage,
# we might not need traditional Django models
# But we can keep this for potential future use with Django's built-in features

class StockWatchlist(models.Model):
    """Optional Django model for user watchlists if needed"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'symbol')
        ordering = ['-added_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.symbol}"