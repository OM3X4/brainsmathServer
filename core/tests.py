import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from .models import Test, Settings
from .serializers import TestSerializer, SettingsSerializer, UserDataSerializer, LeaderboardEntitySerializer


class ModelTests(TestCase):
    """Tests for models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.settings = Settings.objects.create(
            theme='dark',
            font='Arial',
            user=self.user
        )
        self.test = Test.objects.create(
            qpm=50,
            raw=45,
            accuracy=90,
            mode='time',
            difficulty=3,
            number=0,
            time=60000,
            user=self.user
        )

    def test_test_model(self):
        """Test the Test model"""
        self.assertEqual(str(self.test), '50')
        self.assertEqual(self.test.qpm, 50)
        self.assertEqual(self.test.raw, 45)
        self.assertEqual(self.test.accuracy, 90)
        self.assertEqual(self.test.mode, 'time')
        self.assertEqual(self.test.difficulty, 3)
        self.assertEqual(self.test.time, 60000)
        self.assertEqual(self.test.user, self.user)

    def test_settings_model(self):
        """Test the Settings model"""
        self.assertEqual(str(self.settings), 'dark')
        self.assertEqual(self.settings.theme, 'dark')
        self.assertEqual(self.settings.font, 'Arial')
        self.assertEqual(self.settings.user, self.user)


class SerializerTests(TestCase):
    """Tests for serializers"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.settings = Settings.objects.create(
            theme='dark',
            font='Arial',
            user=self.user
        )
        # Create multiple tests with different parameters
        # Time mode tests
        for time in [30000, 60000, 120000, 180000]:
            for difficulty in range(1, 6):
                Test.objects.create(
                    qpm=50 + difficulty * 10,
                    raw=45 + difficulty * 8,
                    accuracy=90,
                    mode='time',
                    difficulty=difficulty,
                    number=0,
                    time=time,
                    user=self.user
                )

        # Questions mode tests
        for number in [5, 10, 15, 25]:
            for difficulty in range(1, 6):
                Test.objects.create(
                    qpm=40 + difficulty * 10,
                    raw=35 + difficulty * 8,
                    accuracy=85,
                    mode='questions',
                    difficulty=difficulty,
                    number=number,
                    time=0,
                    user=self.user
                )

        # Create streak data
        today = datetime.now()
        for i in range(5):
            Test.objects.create(
                qpm=60,
                raw=55,
                accuracy=92,
                mode='time',
                difficulty=3,
                number=0,
                time=60000,
                user=self.user,
                creation=today - timedelta(days=i)
            )

    def test_test_serializer(self):
        """Test the TestSerializer"""
        test = Test.objects.first()
        serializer = TestSerializer(test)

        self.assertIn('qpm', serializer.data)
        self.assertIn('raw', serializer.data)
        self.assertIn('accuracy', serializer.data)
        self.assertIn('mode', serializer.data)
        self.assertIn('difficulty', serializer.data)
        self.assertIn('number', serializer.data)
        self.assertIn('time', serializer.data)
        self.assertIn('user', serializer.data)

    def test_settings_serializer(self):
        """Test the SettingsSerializer"""
        serializer = SettingsSerializer(self.settings)

        self.assertIn('theme', serializer.data)
        self.assertIn('font', serializer.data)
        self.assertIn('user', serializer.data)

    def test_user_data_serializer(self):
        """Test the UserDataSerializer"""
        serializer = UserDataSerializer(self.user)

        self.assertIn('username', serializer.data)
        self.assertIn('streak', serializer.data)
        self.assertIn('date_joined', serializer.data)
        self.assertIn('best_scores', serializer.data)
        self.assertIn('theme', serializer.data)
        self.assertIn('font', serializer.data)
        self.assertIn('tests', serializer.data)

        # Test streak data
        self.assertEqual(serializer.data['streak']['user_streak'], 5)

        # Test best scores
        best_scores = serializer.data['best_scores']
        self.assertIn('time', best_scores)
        self.assertIn('questions', best_scores)

        # Verify time mode best scores
        for time in [30, 60, 120, 180]:
            self.assertIn(str(time), best_scores['time'])
            for difficulty in range(1, 6):
                self.assertIn(str(difficulty), best_scores['time'][str(time)])

        # Verify questions mode best scores
        for question in [5, 10, 15, 25]:
            self.assertIn(str(question), best_scores['questions'])
            for difficulty in range(1, 6):
                self.assertIn(str(difficulty), best_scores['questions'][str(question)])

    def test_leaderboard_entity_serializer(self):
        """Test the LeaderboardEntitySerializer"""
        test = Test.objects.filter(mode='time', time=60000).first()
        serializer = LeaderboardEntitySerializer(test)

        self.assertIn('qpm', serializer.data)
        self.assertIn('raw', serializer.data)
        self.assertIn('accuracy', serializer.data)
        self.assertIn('creation', serializer.data)
        self.assertIn('user', serializer.data)
        self.assertIn('number', serializer.data)
        self.assertIn('mode', serializer.data)
        self.assertIn('time', serializer.data)


class ApiViewTests(APITestCase):
    """Tests for the API views"""

    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpassword123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpassword456'
        )

        # Create settings for users
        Settings.objects.create(
            theme='dark',
            font='Arial',
            user=self.user1
        )
        Settings.objects.create(
            theme='light',
            font='Roboto',
            user=self.user2
        )

        # Create tests for user1
        self.create_tests_for_user(self.user1)
        # Create tests for user2
        self.create_tests_for_user(self.user2)

        # Get tokens for authentication
        refresh = RefreshToken.for_user(self.user1)
        self.access_token_user1 = str(refresh.access_token)

        refresh = RefreshToken.for_user(self.user2)
        self.access_token_user2 = str(refresh.access_token)

    def create_tests_for_user(self, user):
        """Helper method to create test data for a user"""
        # Create time tests
        Test.objects.create(
            qpm=60,
            raw=55,
            accuracy=92,
            mode='time',
            difficulty=3,
            number=0,
            time=60000,
            user=user
        )

        # Create question tests
        Test.objects.create(
            qpm=50,
            raw=45,
            accuracy=90,
            mode='questions',
            difficulty=2,
            number=10,
            time=0,
            user=user
        )

    def test_hi_endpoint(self):
        """Test the hi endpoint"""
        response = self.client.get(reverse('hi'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "hi")

    def test_get_user_data_unauthorized(self):
        """Test getting user data without authentication"""
        response = self.client.get(reverse('user-data'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_data_authorized(self):
        """Test getting user data with authentication"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token_user1}')
        response = self.client.get(reverse('user-data'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser1')
        self.assertEqual(response.data['theme'], 'dark')
        self.assertEqual(response.data['font'], 'Arial')
        self.assertTrue(len(response.data['tests']) > 0)

    def test_update_user_settings(self):
        """Test updating user settings"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token_user1}')
        updated_settings = {
            'theme': 'blue',
            'font': 'Verdana'
        }

        response = self.client.put(
            reverse('user-data'),
            data=json.dumps(updated_settings),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'blue')
        self.assertEqual(response.data['font'], 'Verdana')

        # Check if changes persisted in the database
        settings = Settings.objects.get(user=self.user1)
        self.assertEqual(settings.theme, 'blue')
        self.assertEqual(settings.font, 'Verdana')

    def test_get_leaderboard(self):
        """Test getting the leaderboard"""
        # Create additional data for leaderboard
        Test.objects.create(
            qpm=100,
            raw=95,
            accuracy=95,
            mode='time',
            difficulty=4,
            number=0,
            time=60000,
            user=self.user1
        )

        Test.objects.create(
            qpm=90,
            raw=85,
            accuracy=94,
            mode='time',
            difficulty=4,
            number=0,
            time=60000,
            user=self.user2
        )

        response = self.client.get(reverse('leaderboard'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the leaderboard is ordered by qpm (descending)
        self.assertTrue(response.data[0]['qpm'] >= response.data[1]['qpm'])
        # Check that we have both users in the leaderboard
        user_ids = [item['user'] for item in response.data]
        self.assertIn(self.user1.id, user_ids)
        self.assertIn(self.user2.id, user_ids)

    def test_submit_test_unauthorized(self):
        """Test submitting a test without authentication"""
        test_data = {
            'qpm': 75,
            'raw': 70,
            'accuracy': 93,
            'mode': 'time',
            'difficulty': 3,
            'number': 0,
            'time': 60000
        }

        response = self.client.post(
            reverse('submit-test'),
            data=json.dumps(test_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submit_test_authorized(self):
        """Test submitting a test with authentication"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token_user1}')

        test_data = {
            'qpm': 75,
            'raw': 70,
            'accuracy': 93,
            'mode': 'time',
            'difficulty': 3,
            'number': 0,
            'time': 60000
        }

        response = self.client.post(
            reverse('submit-test'),
            data=json.dumps(test_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['qpm'], 75)
        self.assertEqual(response.data['raw'], 70)
        self.assertEqual(response.data['accuracy'], 93)
        self.assertEqual(response.data['mode'], 'time')
        self.assertEqual(response.data['difficulty'], 3)
        self.assertEqual(response.data['number'], 0)
        self.assertEqual(response.data['time'], 60000)
        self.assertEqual(response.data['user'], self.user1.id)

        # Check if the test was saved to the database
        test = Test.objects.filter(
            qpm=75,
            raw=70,
            user=self.user1
        ).first()

        self.assertIsNotNone(test)
        self.assertEqual(test.accuracy, 93)

    def test_submit_test_invalid_data(self):
        """Test submitting a test with invalid data"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token_user1}')

        # Missing required fields
        test_data = {
            'qpm': 75,
            # Missing other required fields
        }

        response = self.client.post(
            reverse('submit-test'),
            data=json.dumps(test_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StreakCalculationTests(TestCase):
    """Tests specifically for streak calculation logic"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='streakuser',
            password='testpassword123'
        )
        Settings.objects.create(
            theme='dark',
            font='Arial',
            user=self.user
        )

    def test_no_streak(self):
        """Test when there are no tests"""
        serializer = UserDataSerializer(self.user)
        streak_data = serializer.data['streak']

        self.assertEqual(streak_data['user_streak'], 1)
        self.assertEqual(streak_data['longest_streak'], 1)

    def test_consecutive_days_streak(self):
        """Test with tests on consecutive days"""
        today = datetime.now()

        # Create tests for consecutive days
        for i in range(5):
            Test.objects.create(
                qpm=60,
                raw=55,
                accuracy=92,
                mode='time',
                difficulty=3,
                number=0,
                time=60000,
                user=self.user,
                creation=today - timedelta(days=i)
            )

        serializer = UserDataSerializer(self.user)
        streak_data = serializer.data['streak']

        self.assertEqual(streak_data['user_streak'], 5)
        self.assertEqual(streak_data['longest_streak'], 5)

    def test_broken_streak(self):
        """Test with a broken streak"""
        today = datetime.now()

        # Create tests with a gap (missing day 3)
        test_days = [0, 1, 2, 4, 5, 6, 7, 8]
        for i in test_days:
            Test.objects.create(
                qpm=60,
                raw=55,
                accuracy=92,
                mode='time',
                difficulty=3,
                number=0,
                time=60000,
                user=self.user,
                creation=today - timedelta(days=i)
            )

        serializer = UserDataSerializer(self.user)
        streak_data = serializer.data['streak']

        # Current streak should be 3 (days 0, 1, 2)
        # Longest streak should be 5 (days 4, 5, 6, 7, 8)
        self.assertEqual(streak_data['user_streak'], 3)
        self.assertEqual(streak_data['longest_streak'], 5)

    def test_multiple_tests_same_day(self):
        """Test with multiple tests on the same day"""
        today = datetime.now()

        # Create multiple tests for the same days
        for i in range(3):
            for _ in range(3):  # 3 tests per day
                Test.objects.create(
                    qpm=60,
                    raw=55,
                    accuracy=92,
                    mode='time',
                    difficulty=3,
                    number=0,
                    time=60000,
                    user=self.user,
                    creation=today - timedelta(days=i)
                )

        serializer = UserDataSerializer(self.user)
        streak_data = serializer.data['streak']

        # Streak should still be 3, even with multiple tests per day
        self.assertEqual(streak_data['user_streak'], 3)
        self.assertEqual(streak_data['longest_streak'], 3)


class AuthenticationTests(APITestCase):
    """Tests for authentication"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.credentials = {
            'username': 'testuser',
            'password': 'testpassword123'
        }

    def test_jwt_token_obtain(self):
        """Test obtaining JWT token"""
        response = self.client.post(
            reverse('token_obtain_pair'),
            self.credentials,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_refresh(self):
        """Test refreshing JWT token"""
        # First obtain the tokens
        response = self.client.post(
            reverse('token_obtain_pair'),
            self.credentials,
            format='json'
        )

        refresh_token = response.data['refresh']

        # Now try to refresh the access token
        response = self.client.post(
            reverse('token_refresh'),
            {'refresh': refresh_token},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_access_protected_endpoint(self):
        """Test accessing a protected endpoint with a valid token"""
        # Create settings for the user
        Settings.objects.create(
            theme='dark',
            font='Arial',
            user=self.user
        )

        # Get the token
        response = self.client.post(
            reverse('token_obtain_pair'),
            self.credentials,
            format='json'
        )

        access_token = response.data['access']

        # Try to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('user-data'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

