from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, Barcode, Meal, Ingredient
from django.utils import timezone

class RegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Rejestracja nowego użytkownika",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Nazwa użytkownika'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Adres email użytkownika'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Hasło użytkownika'),
            },
            required=['username', 'password']
        ),
        responses={
            201: openapi.Response('User created successfully'),
            400: openapi.Response('Username already exists')
        }
    )
    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            if not username or not password:
                return Response({"error": "Both username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create(
                username=username,
                email=email,
                password=password
            )
            
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Logowanie użytkownika",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Nazwa użytkownika'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Hasło użytkownika'),
            },
            required=['username', 'password']
        ),
        responses={
            200: openapi.Response('Login successful'),
            401: openapi.Response('Invalid credentials')
        }
    )
    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            user = User.objects.filter(username=username, password=password).first()
            if user:
                request.session['user_id'] = user.id
                request.session.save() 
                print(f"User {user.username} logged in with session ID: {request.session.session_key}")
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid username/password."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class MealListView(APIView):
    @swagger_auto_schema(
        operation_description="Pobieranie listy posiłków użytkownika z informacjami o wartościach odżywczych",
        responses={
            200: openapi.Response('Lista posiłków z wartościami odżywczymi'),
            401: openapi.Response('Użytkownik nie jest zalogowany')
        }
    )
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'User not logged in'}, status=401)
        
        meals = Meal.objects.filter(user_id=user_id).order_by('date', 'meal_type')
        data = [
            {
                'id': meal.id,
                'meal_name': meal.meal_name,
                'meal_type': meal.meal_type,
                'date': meal.date,
                'ingredients': [
                    {
                        'id': ing.id,
                        'ingredient_name': ing.ingredient_name,
                        'barcode': ing.barcode,
                        'quantity': ing.quantity,
                        'nutrition': {
                            'calories': ing.total_calories,
                            'protein': ing.total_protein,
                            'fat': ing.total_fat,
                            'carbs': ing.total_carbs,
                            'per_100g': {
                                'calories': ing.calories_per_100g,
                                'protein': ing.protein_per_100g,
                                'fat': ing.fat_per_100g,
                                'carbs': ing.carbs_per_100g
                            }
                        }
                    }
                    for ing in meal.ingredients.all()
                ],
                'total_nutrition': {
                    'calories': sum(ing.total_calories for ing in meal.ingredients.all()),
                    'protein': sum(ing.total_protein for ing in meal.ingredients.all()),
                    'fat': sum(ing.total_fat for ing in meal.ingredients.all()),
                    'carbs': sum(ing.total_carbs for ing in meal.ingredients.all())
                }
            }
            for meal in meals
        ]
        return Response({'meals': data})

    @swagger_auto_schema(
        operation_description="Tworzenie nowego posiłku ze składnikami i ich wartościami odżywczymi",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'meal_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nazwa posiłku'),
                'meal_type': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Typ posiłku',
                    enum=['BREAKFAST', 'LUNCH', 'DINNER']
                ),
                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Data posiłku'),
                'ingredients': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'ingredient_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nazwa składnika'),
                            'barcode': openapi.Schema(type=openapi.TYPE_STRING, description='Kod kreskowy produktu'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Waga w gramach'),
                            'nutrition_per_100g': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'calories': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'protein': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'fat': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'carbs': openapi.Schema(type=openapi.TYPE_NUMBER)
                                }
                            )
                        },
                        required=['ingredient_name', 'quantity']
                    ),
                    description='Lista składników'
                )
            },
            required=['meal_name', 'meal_type', 'ingredients']
        ),
        responses={
            201: openapi.Response('Posiłek został utworzony'),
            400: openapi.Response('Błędne dane lub posiłek tego typu już istnieje dla danej daty'),
            401: openapi.Response('Użytkownik nie jest zalogowany')
        }
    )
    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'User not logged in'}, status=401)

        meal_name = request.data.get('meal_name')
        meal_type = request.data.get('meal_type')
        date = request.data.get('date', timezone.now())
        ingredients_data = request.data.get('ingredients', [])

        if not meal_name or not meal_type or not ingredients_data:
            return Response({
                'error': 'meal_name, meal_type and ingredients are required'
            }, status=400)

        if meal_type not in [choice[0] for choice in Meal.MEAL_TYPES]:
            return Response({
                'error': 'meal_type must be one of: BREAKFAST, LUNCH, DINNER'
            }, status=400)

        if Meal.objects.filter(
            user_id=user_id,
            meal_type=meal_type,
            date__date=timezone.datetime.fromisoformat(date).date() if isinstance(date, str) else date.date()
        ).exists():
            return Response({
                'error': f'A {meal_type.lower()} already exists for this date'
            }, status=400)

        meal = Meal.objects.create(
            user_id=user_id,
            meal_name=meal_name,
            meal_type=meal_type,
            date=date
        )

        ingredients = []
        for ingredient_data in ingredients_data:
            nutrition = ingredient_data.get('nutrition_per_100g', {})
            ingredient = Ingredient.objects.create(
                meal=meal,
                ingredient_name=ingredient_data['ingredient_name'],
                barcode=ingredient_data.get('barcode'),
                quantity=ingredient_data['quantity'],
                calories_per_100g=nutrition.get('calories'),
                protein_per_100g=nutrition.get('protein'),
                fat_per_100g=nutrition.get('fat'),
                carbs_per_100g=nutrition.get('carbs')
            )
            ingredients.append({
                'id': ingredient.id,
                'ingredient_name': ingredient.ingredient_name,
                'barcode': ingredient.barcode,
                'quantity': ingredient.quantity,
                'nutrition': {
                    'calories': ingredient.total_calories,
                    'protein': ingredient.total_protein,
                    'fat': ingredient.total_fat,
                    'carbs': ingredient.total_carbs
                }
            })

        return Response({
            'id': meal.id,
            'meal_name': meal.meal_name,
            'meal_type': meal.meal_type,
            'date': meal.date,
            'ingredients': ingredients,
            'total_nutrition': {
                'calories': sum(ing.total_calories for ing in meal.ingredients.all()),
                'protein': sum(ing.total_protein for ing in meal.ingredients.all()),
                'fat': sum(ing.total_fat for ing in meal.ingredients.all()),
                'carbs': sum(ing.total_carbs for ing in meal.ingredients.all())
            }
        }, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class MealDetailView(APIView):
    def put(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'User not logged in'}, status=401)
        meal = get_object_or_404(Meal, pk=pk, user_id=user_id)
        meal.meal_name = request.data.get('meal_name', meal.meal_name)
        meal.date = request.data.get('date', meal.date)
        meal.save()
        return Response({'message': 'Meal updated'})

    def delete(self, request, pk):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'User not logged in'}, status=401)
        meal = get_object_or_404(Meal, pk=pk, user_id=user_id)
        meal.delete()
        return Response({'message': 'Meal deleted'})

@method_decorator(csrf_exempt, name='dispatch')
class AssignBarcodeView(APIView):
    @swagger_auto_schema(
        operation_description="Przypisywanie kodu kreskowego i makroskładników do zalogowanego użytkownika",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'barcode': openapi.Schema(type=openapi.TYPE_STRING, description='Kod kreskowy'),
                'macros': openapi.Schema(type=openapi.TYPE_OBJECT, description='Dane makroskładników w formacie JSON'),
            },
            required=['barcode', 'macros']
        ),
        responses={200: openapi.Response('Barcode and macros assigned successfully')}
    )
    def post(self, request):
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                print("No user_id in session") 
                return Response({"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

            user = get_object_or_404(User, id=user_id)
            print(f"User {user.username} is logged in")

            barcode = request.data.get('barcode')
            macros = request.data.get('macros')

            print(f"Received barcode: {barcode}")
            print(f"Received macros: {macros}")

            Barcode.objects.create(user=user, barcode=barcode, macros=macros)

            return Response({"message": "Barcode and macros assigned successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class GetUserDataView(APIView):
    @swagger_auto_schema(
        operation_description="Pobieranie wszystkich danych użytkownika (barcode + makroskładniki)",
        responses={200: openapi.Response('List of barcodes and macros')}
    )
    def get(self, request):
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return Response({"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

            user = get_object_or_404(User, id=user_id)

            barcodes = user.barcodes.all()
            barcode_list = [
                {
                    "id": barcode.id,
                    "barcode": barcode.barcode,
                    "macros": barcode.macros
                }
                for barcode in barcodes
            ]

            return Response({"data": barcode_list}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
