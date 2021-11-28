from django.test import Client, TestCase

from .models import Airport, Passenger, Flight 

from django.db.models import Max
# Create your tests here.

class flightstestcase(TestCase):

    def setUp(self):

        # Create airports
        a1 = Airport.objects.create(code="aaa", city="a1")
        a2 = Airport.objects.create(code="bbb", city="a2")

        # Create flights
        Flight.objects.create(origin=a1, destination=a2, duration=100)
        Flight.objects.create(origin=a1, destination=a1, duration=200)
        Flight.objects.create(origin=a1, destination=a2, duration=-100)

    def departures_count(self):
        a = Airport.objects.get(code="aaa")
        self.assertEqual(a.departures.count(), 3)

    def arrivals_count(self):
        a = Airport.objects.get(code="bbb")
        self.assertEqual(a.arrivals.count(), 1)

    def test_valid_flight(self):
        a1 = Airport.objects.get(code="aaa")
        a2 = Airport.objects.get(code="bbb")
        f = Flight.objects.get(origin=a1, destination=a2, duration=100)
        self.assertTrue(f.is_valid_flight())

    def test_invalid_destination(self):
        a1 = Airport.objects.get(code="aaa")
        f = Flight.objects.get(origin=a1, duration=200)
        self.assertFalse(f.is_valid_flight())
    
    def test_valid_duration(self):
        a1 = Airport.objects.get(code="aaa")
        a2 = Airport.objects.get(code="bbb")
        f = Flight.objects.get(origin=a1, destination=a2, duration=-100)
        self.assertFalse(f.is_valid_flight())

    def test_index(self):

        # Set up a client to make requests
        c = Client()

        # send get request to page and store a response
        response = c.get("/flights/")

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)

        # Make sure three flights are returned in the context
        self.assertEqual(response.context["flights"].count(), 3)

    def test_valid_flight_page(self):
        a1 = Airport.objects.get(code="aaa")
        f = Flight.objects.get(origin=a1, destination=a1)

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_flight_page(self):
        max_id = Flight.objects.all().aggregate(Max("id")),["id__max"]

        c = Client()
        response = c.get("/flights/{max_id + 1}")
        self.assertEqual(response.status_code, 404)

    def test_flight_page_passengers(self):
        f = Flight.objects.get(pk=1)
        p = Passenger.objects.create(first="Alice", last="Adams")
        f.passengers.add(p)

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["passengers"].count(), 1)

    def test_flight_page_non_passengers(self):
        f = Flight.objects.get(pk=1)
        p = Passenger.objects.create(first="Alice", last="Adams")

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["non_passengers"].count(), 1)