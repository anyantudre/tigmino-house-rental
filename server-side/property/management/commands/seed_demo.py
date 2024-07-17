"""Fill the database with demo users, listings, bookings, favorites and conversations.

Usage, from server-side/:
    python manage.py seed_demo           # only if the database has no listings yet
    python manage.py seed_demo --reset   # delete all users and listings first

Every demo account uses the password below. The photos and avatars it points to
are in media/uploads/ (see docs/CREDITS.md).
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from chat.models import Conversation, ConversationMessage
from property.models import Property, Reservation
from useraccount.models import User

DEMO_PASSWORD = "tigmino-demo"
TIGMINO_FEE = 0.05

# key: (name, city, phone, staff)
USERS = {
    "sara": ("Sara Bennani", "Rabat", "+212 600 000 101", False),
    "yasmine": ("Yasmine El Idrissi", "Marrakech", "+212 600 000 102", False),
    "karim": ("Karim Benali", "Fes", "+212 600 000 103", False),
    "salma": ("Salma Ouazzani", "Chefchaouen", "+212 600 000 104", False),
    "youssef": ("Youssef Amrani", "Agadir", "+212 600 000 105", False),
    "nadia": ("Nadia Tazi", "Rabat", "+212 600 000 106", False),
    "omar": ("Omar Lahlou", "Safi", "+212 600 000 107", False),
    "hassan": ("Hassan Ait Brahim", "Errachidia", "+212 600 000 108", False),
    "amina": ("Amina Diallo", "Safi", "+212 600 000 109", False),
    "ibrahim": ("Ibrahim Ouedraogo", "Casablanca", "+212 600 000 110", False),
    "lea": ("Léa Martin", "Lyon", "+33 600 000 111", False),
    "mehdi": ("Mehdi Alaoui", "Tangier", "+212 600 000 112", False),
    "admin": ("TIGMINO Admin", "Safi", "+212 600 000 100", True),
}

# (key, host, title, city, category, price, bedrooms, bathrooms, guests, area m², number of photos, description)
LISTINGS = [
    ("riad-marrakech", "yasmine", "Riad with a pool in the Marrakech medina", "Marrakech", "villas", 1250, 4, 4, 8, 260, 3,
     "A traditional riad ten minutes on foot from Jemaa el-Fna. The four bedrooms open onto a planted courtyard "
     "with a small pool, and breakfast is served on the roof terrace. Good for families and groups of friends."),
    ("duplex-gueliz", "yasmine", "Bright duplex in Gueliz with WiFi and AC", "Marrakech", "villas", 660, 2, 2, 4, 110, 1,
     "A modern duplex in Gueliz, close to cafés, shops and the tram. Air conditioning in every room, fast WiFi, "
     "a full kitchen and access to the residence pool."),
    ("villa-palmeraie", "yasmine", "Villa with a garden in the Palmeraie", "Marrakech", "villas", 1900, 5, 4, 10, 420, 1,
     "A large villa among the palm trees, 20 minutes from the city centre. Private pool, garden, outdoor dining "
     "area and parking. Ideal for family gatherings."),
    ("riad-fes", "karim", "Courtyard riad near Bab Boujloud", "Fes", "villas", 890, 3, 3, 6, 180, 2,
     "A restored riad with zellij tiles and a fountain courtyard, a short walk from Bab Boujloud. Karim can "
     "arrange a guide for the medina and a pick-up from the train station."),
    ("studio-fes", "karim", "Quiet studio in the Fes ville nouvelle", "Fes", "tiny_homes", 199, 1, 1, 2, 32, 1,
     "A small, well-equipped studio near Avenue Hassan II. Kitchenette, washing machine and WiFi. "
     "Popular with students and long stays."),
    ("chefchaouen-house", "salma", "Blue house in the Chefchaouen medina", "Chefchaouen", "tiny_homes", 420, 2, 1, 4, 70, 2,
     "A small traditional house in the blue streets, five minutes from Outa el Hammam square. "
     "The rooftop looks over the mountains."),
    ("chefchaouen-farm", "salma", "Farm stay outside Chefchaouen", "Chefchaouen", "cabins", 520, 3, 2, 6, 140, 1,
     "A family farm in the hills, 15 minutes by car from the medina. Home-cooked meals with produce from the "
     "garden, hiking trails from the door and a sunflower field in summer."),
    ("taghazout-surf", "youssef", "Surf house in Taghazout village", "Taghazout", "beach", 750, 3, 2, 6, 120, 2,
     "A colourful house in the village, a two-minute walk from the waves. Board storage, an outdoor shower and a "
     "terrace facing the ocean. Youssef can book lessons with local surf schools."),
    ("agadir-jacuzzi", "youssef", "Agadir apartment with a jacuzzi, near the beach", "Agadir", "beach", 559, 1, 1, 2, 65, 3,
     "A one-bedroom apartment with an in-room jacuzzi, five minutes from the corniche. Air conditioning, "
     "Smart TV and a secure residence with parking."),
    ("agadir-rooftop", "youssef", "Rooftop pool apartment in Agadir", "Agadir", "beach", 1099, 3, 2, 6, 150, 1,
     "A top-floor apartment with its own rooftop pool and sun loungers. Close to the marina and the beach, "
     "with a fully equipped kitchen."),
    ("rabat-oudayas", "nadia", "White house in the Kasbah of the Udayas", "Rabat", "tiny_homes", 480, 2, 1, 3, 60, 3,
     "A small house in the white and blue lanes of the Kasbah, above the Bouregreg river. Walk to the Andalusian "
     "gardens, the medina and the beach."),
    ("casablanca-artdeco", "nadia", "Art Deco apartment on Boulevard Mohammed V", "Casablanca", "tiny_homes", 540, 2, 1, 4, 85, 1,
     "A renovated apartment in a 1930s building in the city centre, close to the tram, the Central Market and "
     "the train station. High ceilings, balcony and fast WiFi."),
    ("asilah-seafront", "omar", "Seafront house in the Asilah medina", "Asilah", "beach", 640, 2, 2, 4, 90, 2,
     "A white house on the ramparts with a sea-view terrace. The beach is a ten-minute walk away and the medina's "
     "murals are on your doorstep."),
    ("essaouira-riad", "omar", "Riad with a patio in Essaouira", "Essaouira", "beach", 710, 4, 3, 8, 200, 2,
     "A riad with galleries around a shaded patio, near the ramparts and the fishing port. Five minutes from the "
     "beach, where the wind is good for kitesurfing."),
    ("merzouga-camp", "hassan", "Desert camp in the Merzouga dunes", "Merzouga", "cabins", 650, 1, 1, 2, 30, 2,
     "A private Berber tent at the foot of the Erg Chebbi dunes, with a real bed and a bathroom. Dinner, breakfast "
     "and a sunset camel ride are included."),
    ("ifrane-chalet", "hassan", "Stone chalet near Ifrane", "Ifrane", "cabins", 980, 3, 2, 6, 160, 1,
     "A stone chalet surrounded by cedar forest, 10 minutes from Ifrane. Fireplace, garden and barbecue; "
     "the Michlifen ski slopes are 20 minutes away in winter."),
    ("safi-studio", "omar", "Student studio near ENSA Safi", "Safi", "tiny_homes", 180, 1, 1, 1, 28, 1,
     "A furnished studio close to the university campus, with a desk, WiFi and a kitchenette. "
     "Monthly stays are welcome."),
]

# (guest, listing, start offset in days from today, nights, guests)
RESERVATIONS = [
    ("sara", "taghazout-surf", 12, 4, 2),
    ("sara", "chefchaouen-house", -60, 3, 2),
    ("amina", "safi-studio", -20, 30, 1),
    ("ibrahim", "merzouga-camp", 25, 2, 2),
    ("lea", "riad-fes", 8, 5, 4),
    ("lea", "riad-marrakech", -120, 4, 6),
    ("mehdi", "asilah-seafront", 40, 3, 3),
    ("mehdi", "ifrane-chalet", -40, 2, 4),
    ("amina", "essaouira-riad", 55, 3, 5),
    ("ibrahim", "casablanca-artdeco", -10, 2, 1),
]

FAVORITES = {
    "sara": ["riad-marrakech", "asilah-seafront", "ifrane-chalet", "merzouga-camp"],
    "amina": ["safi-studio", "studio-fes", "rabat-oudayas"],
    "lea": ["riad-fes", "chefchaouen-farm", "essaouira-riad"],
    "mehdi": ["asilah-seafront", "taghazout-surf"],
    "ibrahim": ["merzouga-camp", "villa-palmeraie"],
}

# (guest, host, minutes ago when the conversation started, [(sender, text), ...])
CONVERSATIONS = [
    ("sara", "yasmine", 60 * 26, [
        ("sara", "Hello Yasmine! Is the riad free for the first weekend of next month? We would be 6 adults."),
        ("yasmine", "Hello Sara, yes, those dates are still free. The riad sleeps up to 8, so 6 is perfect."),
        ("sara", "Great. Is breakfast included?"),
        ("yasmine", "Yes, a Moroccan breakfast is served on the terrace every morning, from 8 to 11."),
        ("sara", "And can you organise a transfer from the airport?"),
        ("yasmine", "Of course. My driver can pick you up for 150 MAD per trip. Just send me your flight number."),
        ("sara", "Perfect, thank you! I'll book tonight."),
    ]),
    ("sara", "youssef", 60 * 5, [
        ("youssef", "Hi Sara, thanks for booking the surf house! Do you need boards or lessons?"),
        ("sara", "Hi Youssef! Two boards would be great, we are beginners."),
        ("youssef", "No problem. I'll book a 2-hour lesson for your first morning. The waves are small this month."),
        ("sara", "Sounds good. What time can we check in?"),
        ("youssef", "Any time after 2 pm. I'll leave the key with my neighbour Hamid if I'm at the beach."),
    ]),
    ("sara", "salma", 60 * 24 * 58, [
        ("sara", "Thank you Salma, we loved the blue house. The view from the roof is beautiful!"),
        ("salma", "Thank you Sara, you were great guests. Come back in spring when the hills are green."),
    ]),
    ("amina", "omar", 60 * 24 * 25, [
        ("amina", "Good morning, I'm a student at ENSA Safi. Can I rent the studio for a whole month?"),
        ("omar", "Good morning Amina, yes, monthly stays are welcome. WiFi and water are included."),
        ("amina", "Is there a desk? I have exams soon."),
        ("omar", "Yes, there is a desk by the window and a quiet street. Good luck with your exams!"),
    ]),
    ("lea", "karim", 60 * 30, [
        ("lea", "Bonjour Karim, we arrive by train at 6 pm. Is that okay for check-in?"),
        ("karim", "Bonjour Léa, of course. I'll meet you at the station and walk you to the riad."),
        ("lea", "Merci! Could you also recommend a guide for the medina?"),
        ("karim", "My cousin Driss is an official guide. A half-day tour is 300 MAD for the group."),
    ]),
    ("ibrahim", "hassan", 60 * 50, [
        ("ibrahim", "Hello Hassan, how do we get to the camp from Merzouga?"),
        ("hassan", "Hello Ibrahim! Park at my guesthouse in the village; the camel ride to the camp takes about an hour."),
        ("ibrahim", "Can we watch the sunrise from the dunes?"),
        ("hassan", "Yes, we wake up at 6 and climb the big dune together. Bring a warm jacket, nights are cold."),
    ]),
]


class Command(BaseCommand):
    help = "Create demo users, listings, bookings, favorites and conversations."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete all existing users and listings first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Conversation.objects.all().delete()
            Property.objects.all().delete()
            User.objects.all().delete()
        elif Property.objects.exists():
            self.stdout.write("The database already has listings. Use --reset to replace them.")
            return

        users = {}
        for key, (name, city, phone, staff) in USERS.items():
            user = User.objects.create_user(
                name=name,
                email=f"{key}@example.com",
                password=DEMO_PASSWORD,
                username=key,
                city=city,
                phone=phone,
                is_staff=staff,
                is_superuser=staff,
            )
            user.avatar.name = f"uploads/avatars/{key}.png"
            user.save(update_fields=["avatar"])
            users[key] = user

        properties = {}
        for key, host, title, city, category, price, bedrooms, bathrooms, guests, area, photos, description in LISTINGS:
            prop = Property(
                title=title, description=description, price_per_night=price, bedrooms=bedrooms,
                bathrooms=bathrooms, guests=guests, area=area, city=city, category=category,
                landlord=users[host],
            )
            prop.image.name = f"uploads/properties/{key}-1.webp"
            for slot in range(2, photos + 1):
                getattr(prop, f"image{slot - 1}").name = f"uploads/properties/{key}-{slot}.webp"
            prop.save()
            properties[key] = prop

        today = date.today()
        for guest, listing, start, nights, n_guests in RESERVATIONS:
            prop = properties[listing]
            start_date = today + timedelta(days=start)
            Reservation.objects.create(
                property=prop, created_by=users[guest], guests=n_guests,
                start_date=start_date, end_date=start_date + timedelta(days=nights), number_of_nights=nights,
                total_price=round(prop.price_per_night * nights * (1 + TIGMINO_FEE), 2),
            )

        for guest, listings in FAVORITES.items():
            for listing in listings:
                properties[listing].favorited.add(users[guest])

        now = timezone.now()
        for guest, host, minutes_ago, messages in CONVERSATIONS:
            conversation = Conversation.objects.create()
            conversation.users.add(users[guest], users[host])
            sent_at = now - timedelta(minutes=minutes_ago)
            for sender, text in messages:
                recipient = host if sender == guest else guest
                message = ConversationMessage.objects.create(
                    conversation=conversation, body=text, created_by=users[sender], sent_to=users[recipient])
                ConversationMessage.objects.filter(pk=message.pk).update(created_at=sent_at)
                sent_at += timedelta(minutes=7)
            Conversation.objects.filter(pk=conversation.pk).update(created_at=now - timedelta(minutes=minutes_ago),
                                                                   modified_at=sent_at)

        self.stdout.write(self.style.SUCCESS(
            f"Created {len(users)} users, {len(properties)} listings, {len(RESERVATIONS)} reservations "
            f"and {len(CONVERSATIONS)} conversations. Password for every account: {DEMO_PASSWORD}"))
