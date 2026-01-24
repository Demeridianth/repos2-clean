import pandas as pd
from django.core.management.base import BaseCommand
from oilprices.models import OilPrice
from datetime import datetime

class Command(BaseCommand):
    help = "Load oil prices from CSV into database"

    def handle(self, *args, **options):
        df = pd.read_csv("oilprices/data/oil.csv")

        df.columns = ["price_date", "price"]
        df["euro_price"] = df["price"] * 1.1
        df = df.fillna(0).head(5)

        created = 0
        for _, row in df.iterrows():
            OilPrice.objects.create(
                price_date=row["price_date"],
                price=row["price"],
                euro_price=row["euro_price"],
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully loaded {created} oil prices")
        )
