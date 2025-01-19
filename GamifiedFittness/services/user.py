from django.db import connection

def get_top_users_summary():
    print("here")
    query = """
    (
        SELECT user_id, SUM(points) AS total_points, SUM(calories) AS total_calories
        FROM GamifiedFittness_useractivity
        GROUP BY user_id
    )
    UNION ALL
    (
        SELECT user_id, 
               SUM(challenge.points * userchallenge.progress) AS total_points,
               SUM(challenge.calories * userchallenge.progress) AS total_calories
        FROM GamifiedFittness_userchallenge
        JOIN GamifiedFittness_challenge AS challenge ON userchallenge.challenge_id = challenge.id
        GROUP BY user_id
    )
    LIMIT 10
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    print(results)
    formatted_results = [
        {"user_id": row[0], "total_points": row[1], "total_calories": row[2]} for row in results
    ]
    return formatted_results

