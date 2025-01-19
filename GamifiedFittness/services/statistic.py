from django.db import connection


def get_statistics():
    query = """
    SELECT 
        GamifiedFittness_activity.name,
        COUNT(*)
        FROM 
            GamifiedFittness_activity 
        LEFT JOIN 
            GamifiedFittness_useractivity 
        ON 
            GamifiedFittness_activity.id = GamifiedFittness_useractivity.activity_id
        GROUP BY 
            GamifiedFittness_activity.id;

    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    except Exception as e:
            print(str(e))
            return {"success": False, "message": "Could not be Load"} 
    
      
    formatted_results = [
        {"Activity": row[0], "Count": row[1]} for row in results
    ]

    return {"success": True, "message": "Loaded", "data": formatted_results}
   


