from django.db import connection

def get_top_users_summary():
    query = """
    SELECT user_id, user.username, SUM(points) AS total_points, SUM(calories) AS total_calories
        FROM (
            SELECT user_id, points, calories
            FROM GamifiedFittness_useractivity
            UNION ALL
            SELECT user_id, (challenge.points * progress) AS points, 
                (challenge.calories * progress) AS calories
            FROM GamifiedFittness_userchallenge
            JOIN GamifiedFittness_challenge AS challenge
            ON GamifiedFittness_userchallenge.challenge_id = challenge.id
        ) AS combined_data
        JOIN GamifiedFittness_user AS user
        ON user.id = combined_data.user_id
        GROUP BY user_id
        LIMIT 10
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    except Exception as e:
            return {"success": False, "message": "Could not be Load"} 
      
    formatted_results = [
        {"user_id": row[0], "user_name": row[1], "total_points": round(row[2],2), "total_calories": round(row[3],2) } for row in results
    ]

    return {"success": True, "message": "Loaded", "data": formatted_results}   

